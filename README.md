# SoundCloud to Apple Music Sync

Download SoundCloud playlists and automatically sync them to Apple Music on macOS.

## Features

- Download entire SoundCloud playlists as MP3 files
- Automatically create playlists in Apple Music
- Add downloaded songs to your Apple Music library
- Save configuration for easy re-syncing
- Real-time sync status and terminal output

## Requirements

- macOS (Intel or Apple Silicon)
- Python 3.9+
- Apple Music App is OPEN when using sync tool

## Installation

1. Download the latest DMG file
2. Drag the app to your Applications folder
3. Run the app

## First Time Setup

Opening the app on mac

macOS will block apps from unidentified developers by default. if this happens:

1. open System Settings → Privacy & Security
2. under Security, you’ll see a message about the app being blocked
3. click Open Anyway
4. confirm you want to open it


## How to Use

Before you start
Make sure Apple Music is open.

To sync across your devices:

   - Open Apple Music
   - Go to Music → Settings → General
   - Turn on “Sync Library”

DIRECTIONS ON TOP RIGHT OF APP (these are rewritten)

1. Get your SoundCloud token:

2. Enter your SoundCloud token in the app

3. Paste your SoundCloud playlist URL

4. Create a NEW folder for each album (important: don't reuse folders)

5. Enter the album name and artist

6. Click "Start Sync"

7. Check Apple Music for your new songs

8. After a few minutes songs should be synced to your other devices using same icloud (iPhone and ipad)

## Important

Each album MUST have its own download folder. If you sync different playlists to the same folder, songs will be re-added to Apple Music and create duplicates.


If songs don't appear in Apple Music, check:
- Your SoundCloud token is correct
- Your playlist URL is direct (not a search)
- Your download folder has songs in it
- Apple Music app is running

## License

MIT
