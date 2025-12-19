#!/usr/bin/env python3
"""
Spotify Playlist Scraper
Scrapes playlist names and song lists from Spotify playlists.
"""

import os
import re
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

def find_firefox_profile():
    """Find the default Firefox profile directory."""
    home = Path.home()
    
    # Linux Firefox profile location
    firefox_dir = home / ".mozilla" / "firefox"
    
    if not firefox_dir.exists():
        return None
    
    # Look for profiles.ini to find default profile
    profiles_ini = firefox_dir / "profiles.ini"
    if profiles_ini.exists():
        with open(profiles_ini, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('Path=') and 'default-release' in line.lower():
                    profile_path = line.split('=')[1].strip()
                    full_path = firefox_dir / profile_path
                    if full_path.exists():
                        return str(full_path)
    
    # Fallback: find any .default-release profile
    for item in firefox_dir.iterdir():
        if item.is_dir() and '.default-release' in item.name:
            return str(item)
    
    # Last resort: find any .default profile
    for item in firefox_dir.iterdir():
        if item.is_dir() and '.default' in item.name:
            return str(item)
    
    return None



def sanitize_folder_name(name):
    """Remove invalid characters from folder name."""
    # Remove or replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    # Limit length
    if len(name) > 200:
        name = name[:200]
    return name if name else "Untitled_Playlist"


def setup_firefox_driver(profile_path=None):
    """Set up Firefox WebDriver with user profile."""
    options = Options()
    
    if profile_path:
        print(f"Using Firefox profile: {profile_path}")
        options.add_argument('-profile')
        options.add_argument(profile_path)
    
    # Install and use geckodriver
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    
    return driver


def scrape_playlist(driver, playlist_url):
    """Scrape playlist name and songs from Spotify."""
    print(f"Navigating to: {playlist_url}")
    driver.get(playlist_url)
    
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Waiting for playlist to load...")
        
        # Try multiple selectors to find the playlist name
        selectors = [
            "div[data-testid='playlist-page'] h1",  # Main playlist page header
            "div[data-testid='entity-page'] h1",    # Alternative entity page
            "h1[data-encore-id='type']",             # Encore ID type
            "div.main-view-container h1",            # Main view container
            "section[data-testid='playlist-page'] h1",  # Section variant
        ]
        
        playlist_name = None
        for selector in selectors:
            try:
                playlist_name_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                playlist_name = playlist_name_element.text.strip()
                
                # Make sure we didn't grab "Your Library" or other sidebar text
                if playlist_name and playlist_name not in ["Your Library", "Library", ""]:
                    print(f"Playlist found: {playlist_name}")
                    break
                else:
                    playlist_name = None
            except (TimeoutException, NoSuchElementException):
                continue
        
        if not playlist_name:
            raise Exception("Could not find playlist name with any selector")
            
    except Exception as e:
        print(f"Could not find playlist name. Error: {e}")
        print("Trying to extract from page title...")
        try:
            # Last resort: try to get from page title
            page_title = driver.title
            # Spotify titles are usually "Playlist Name - playlist by User | Spotify"
            if " - " in page_title:
                playlist_name = page_title.split(" - ")[0].strip()
                print(f"Playlist found from title: {playlist_name}")
            else:
                print("Error: Could not find playlist name")
                return None, []
        except:
            print("Error: Could not find playlist name")
            return None, []
    
    # Scroll down the page to load all songs dynamically
    print("Scrolling to load all songs...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_scrolls = 50
    
    while scroll_attempts < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        
        last_height = new_height
        scroll_attempts += 1
        
        if scroll_attempts % 5 == 0:
            print(f"  Scrolled {scroll_attempts} times...")
    
    print("Extracting songs...")
    
    songs = []
    
    # Detect the "Recommended" section to exclude those songs
    recommended_section_start = None
    try:
        recommended_selectors = [
            "//h2[contains(translate(text(), 'RECOMMENDED', 'recommended'), 'recommended')]",
            "//div[contains(translate(@aria-label, 'RECOMMENDED', 'recommended'), 'recommended')]",
            "//*[contains(translate(text(), 'RECOMMENDED', 'recommended'), 'recommended')]"
        ]
        
        for selector in recommended_selectors:
            try:
                recommended_element = driver.find_element(By.XPATH, selector)
                recommended_section_start = recommended_element
                print("Found 'Recommended' section - will exclude these songs")
                break
            except:
                continue
    except:
        pass
    
    # Find all song row elements
    song_selectors = [
        "div[data-testid='tracklist-row']",
        "div[data-testid='playlist-tracklist'] div[role='row']",
        "div.tracklist-row"
    ]
    
    song_elements = []
    for selector in song_selectors:
        try:
            song_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if song_elements:
                print(f"Found {len(song_elements)} song elements using selector: {selector}")
                break
        except:
            continue
    
    if not song_elements:
        print("Warning: Could not find song elements")
        return playlist_name, []
    
    # Extract song and artist names from each row
    for idx, element in enumerate(song_elements, 1):
        try:
            # Stop processing if we've reached the recommended section
            if recommended_section_start:
                element_y = element.location['y']
                recommended_y = recommended_section_start.location['y']
                
                if element_y >= recommended_y:
                    print(f"Stopping at song {idx} - reached 'Recommended' section")
                    break
            
            song_name = None
            artist_name = None
            
            # Extract song name using multiple selector strategies
            try:
                song_name_elem = element.find_element(By.CSS_SELECTOR, "div[data-testid='tracklist-row'] a[data-testid='internal-track-link']")
                song_name = song_name_elem.text
            except:
                try:
                    song_name_elem = element.find_element(By.CSS_SELECTOR, "a[data-testid='internal-track-link']")
                    song_name = song_name_elem.text
                except:
                    pass
            
            # Extract artist name
            try:
                artist_elem = element.find_element(By.CSS_SELECTOR, "span[data-testid='internal-track-link'] a")
                artist_name = artist_elem.text
            except:
                try:
                    artist_links = element.find_elements(By.CSS_SELECTOR, "a")
                    if len(artist_links) > 1:
                        artist_name = artist_links[1].text
                except:
                    pass
            
            if song_name:
                if artist_name:
                    song_info = f"{song_name} - {artist_name}"
                else:
                    song_info = song_name
                
                songs.append(song_info)
                
                if idx % 10 == 0:
                    print(f"  Extracted {idx} songs...")
        except Exception as e:
            # Skip elements that can't be parsed
            continue
    
    print(f"Successfully extracted {len(songs)} songs")
    return playlist_name, songs


def save_playlist(playlist_name, songs):
    """Save playlist songs to a text file in Downloads folder."""
    downloads_dir = Path.home() / "Downloads"
    
    # Create sanitized folder name
    folder_name = sanitize_folder_name(playlist_name)
    playlist_folder = downloads_dir / folder_name
    
    # Create folder
    playlist_folder.mkdir(exist_ok=True)
    print(f"Created folder: {playlist_folder}")
    
    # Save songs to text file
    output_file = playlist_folder / "songs.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Playlist: {playlist_name}\n")
        f.write(f"Total Songs: {len(songs)}\n")
        f.write("=" * 50 + "\n\n")
        
        for idx, song in enumerate(songs, 1):
            f.write(f"{idx}. {song}\n")
    
    print(f"Saved {len(songs)} songs to: {output_file}")
    return output_file


def main():
    """Main function to run the Spotify scraper."""
    print("=" * 60)
    print("Spotify Playlist Scraper")
    print("=" * 60)
    
    # Find Firefox profile
    profile_path = find_firefox_profile()
    
    if profile_path:
        print(f"\nFound Firefox profile for logged-in session")
        print("⚠️  Make sure Firefox is closed to avoid profile lock issues.")
        input("Press Enter to continue...")
    else:
        print("\nWarning: Could not find Firefox profile.")
        print("The scraper will only work with public playlists.")
    
    driver = None
    try:
        # Set up Firefox driver with profile
        print("\nLaunching Firefox...")
        driver = setup_firefox_driver(profile_path)
        
        # Loop to allow multiple playlist downloads
        while True:
            # Get playlist URL from user
            playlist_url = input("\nEnter Spotify playlist URL: ").strip()
            
            if not playlist_url:
                print("Error: No URL provided")
                continue
            
            try:
                # Scrape playlist
                playlist_name, songs = scrape_playlist(driver, playlist_url)
                
                if not playlist_name:
                    print("\nError: Could not scrape playlist")
                    # Ask if user wants to try another URL
                    retry = input("\nWould you like to try another playlist? (y/n): ").strip().lower()
                    if retry != 'y':
                        break
                    continue
                
                if not songs:
                    print("\nWarning: No songs found in playlist")
                    print("\nPossible reasons:")
                    print("  - The playlist is private")
                    print("  - Spotify's page structure has changed")
                    print("  - The page didn't load completely")
                    # Ask if user wants to try another URL
                    retry = input("\nWould you like to try another playlist? (y/n): ").strip().lower()
                    if retry != 'y':
                        break
                    continue
                
                # Save to file
                print("\nSaving playlist...")
                output_file = save_playlist(playlist_name, songs)
                
                print("\n" + "=" * 60)
                print("SUCCESS!")
                print(f"Playlist: {playlist_name}")
                print(f"Songs saved to: {output_file}")
                print("=" * 60)
                
                # Ask if user wants to download another playlist
                another = input("\nWould you like to download another playlist? (y/n): ").strip().lower()
                if another != 'y':
                    print("\nExiting...")
                    break
                    
            except Exception as e:
                print(f"\nError occurred while scraping: {e}")
                import traceback
                traceback.print_exc()
                
                # Ask if user wants to try another URL
                retry = input("\nWould you like to try another playlist? (y/n): ").strip().lower()
                if retry != 'y':
                    break
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
