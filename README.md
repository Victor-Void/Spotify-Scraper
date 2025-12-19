# Spotify Playlist Scraper

A Python script that scrapes Spotify playlists and saves song lists to organized text files. Works with both public and private playlists by using your Firefox browser profile.

## ✨ Features

- 🔐 **Access Private Playlists** - Uses your Firefox profile with Spotify login
- 🔄 **Multiple Playlists** - Download multiple playlists in one session
- 📝 **Complete Song Info** - Scrapes song names and artist names
- 📁 **Auto-Organization** - Creates folders in Downloads with playlist names
- 💾 **Text Export** - Saves songs to `.txt` files
- 🎯 **Smart Filtering** - Excludes "Recommended" section songs
- 🔄 **Dynamic Scrolling** - Handles large playlists automatically
- 🛡️ **Robust** - Multiple selector fallbacks and error handling

## 📋 Requirements

- **Python 3.7+**
- **Firefox Browser** (installed and set up)
- **Spotify Account** (logged into Firefox for private playlists)

## 🚀 Quick Start

### 1. Clone or Download

```bash
git clone https://github.com/Victor-Void/Spotify-Scraper.git
cd Spotify-Scraper
```

Or download and extract the ZIP file.

### 2. Install Python Dependencies

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Scraper

**Important:** Close Firefox before running to avoid profile lock issues!

```bash
python main.py
```

## 📖 Usage

1. **Start the script:**
   ```bash
   python main.py
   ```

2. **Enter a Spotify playlist URL** when prompted:
   ```
   Enter Spotify playlist URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   ```

3. **Wait for scraping** - The script will:
   - Launch Firefox with your profile
   - Navigate to the playlist
   - Scroll to load all songs
   - Extract song and artist names
   - Save to `~/Downloads/[Playlist Name]/songs.txt`

4. **Download more playlists** - After completion, you'll be prompted:
   ```
   Would you like to download another playlist? (y/n):
   ```
   - Type `y` to download another playlist
   - Type `n` to exit and close the browser

## 📂 Output Format

Songs are saved in `~/Downloads/[Playlist Name]/songs.txt`:

```
Playlist: My Awesome Playlist
Total Songs: 50
==================================================

1. Song Title - Artist Name
2. Another Song - Another Artist
3. Third Song - Third Artist
...
```

## 🔧 Platform-Specific Notes

### Linux
- Firefox profile is automatically detected from `~/.mozilla/firefox/`
- Works out of the box if Firefox is installed normally

### Windows
- The script is designed for Linux but can be adapted
- You may need to modify the `find_firefox_profile()` function
- Firefox profile location: `%APPDATA%\Mozilla\Firefox\Profiles\`

### macOS
- Firefox profile location: `~/Library/Application Support/Firefox/Profiles/`
- May need to modify the `find_firefox_profile()` function

## 🐛 Troubleshooting

### "Profile lock" error
- **Solution:** Make sure Firefox is completely closed before running the script

### "Could not find Firefox profile"
- **Solution:** The script will still work with public playlists
- For private playlists, ensure Firefox is installed and you've used it at least once

### "No songs found"
- **Possible causes:**
  - Playlist is private and you're not logged in
  - Spotify changed their page structure
  - Page didn't load completely
- **Solution:** Try running again, or check if you can access the playlist in Firefox manually

### GeckoDriver issues
- **Solution:** The script auto-downloads GeckoDriver via `webdriver-manager`
- If issues persist, manually download from [Mozilla's releases](https://github.com/mozilla/geckodriver/releases)

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements!

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for personal use only. Please respect Spotify's Terms of Service and use responsibly. Do not use this for commercial purposes or to redistribute copyrighted content.

## 🎯 Tips

- **Large Playlists:** The script handles scrolling automatically, but very large playlists (1000+ songs) may take a few minutes
- **Private Playlists:** Make sure you're logged into Spotify in Firefox
- **Multiple Sessions:** You can download as many playlists as you want in one session
- **Folder Names:** Special characters in playlist names are automatically sanitized for filesystem compatibility
