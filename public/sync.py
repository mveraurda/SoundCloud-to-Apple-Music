#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import ssl
import urllib3
from pathlib import Path

# Auto-install required packages on first run
marker = os.path.expanduser('~/.soundcloud_sync_initialized')
if not os.path.exists(marker):
    packages = ['scdl', 'yt-dlp', 'ffmpeg-python']
    print("Setting up required packages (first time only)...")
    
    # Use the same Python executable that's running this script
    python_exe = sys.executable
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"{pkg} already installed")
        except ImportError:
            print(f"Installing {pkg}...")
            try:
                subprocess.check_call([python_exe, '-m', 'pip', 'install', pkg, '--break-system-packages', '--quiet'])
                print(f"{pkg} installed successfully")
            except Exception as e:
                print(f"Failed to install {pkg}: {e}")
    
    # Create marker file to skip this next time
    os.makedirs(os.path.dirname(marker), exist_ok=True)
    with open(marker, 'w') as f:
        f.write('initialized')
    print("Setup complete! You won't see this message again.")

# Fix SSL issues
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except:
    pass

def download_playlist(auth_token, playlist_url, download_path):
    """Download SoundCloud playlist using scdl"""
    print("Downloading playlist from SoundCloud...")
    print(f"URL: {playlist_url}")
    print(f"Path: {download_path}")
    
    os.makedirs(download_path, exist_ok=True)
    
    try:
        from scdl.scdl import _main
        print("scdl module found")
        sys.argv = ['scdl', '-l', playlist_url, '--auth-token', auth_token, '--path', download_path, '--onlymp3']
        _main()
        print("Download successful!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_apple_music_songs():
    """Get list of songs in Apple Music library"""
    print("Checking Apple Music library...")
    applescript = 'tell application "Music" to return count of tracks'
    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        count = int(result.stdout.strip())
        print(f"Found {count} songs in Apple Music library")
        return count
    except:
        print("Found 0 songs in Apple Music library")
        return 0

def create_playlist(name):
    """Create a new playlist in Apple Music"""
    print(f"Creating playlist: {name}")
    applescript = f'tell application "Music" to make new playlist with properties {{name:"{name}"}}'
    try:
        subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        print(f"Playlist created: {name}")
        return True
    except:
        print("Failed to create playlist")
        return False

def add_songs_to_apple_music(folder_path, playlist_name, album_artist):
    """Add downloaded songs to Apple Music and playlist"""
    mp3_files = sorted(Path(folder_path).rglob('*.mp3'))
    print(f"Total files found: {len(mp3_files)}")
    
    if not mp3_files:
        print("No files downloaded - check auth token and URL")
        return
    
    for mp3_file in mp3_files:
        try:
            if album_artist:
                cmd = f'ffmpeg -i "{mp3_file}" -metadata album_artist="{album_artist}" -c copy "{mp3_file}.tmp" -y'
                result = subprocess.run(cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    os.replace(f"{mp3_file}.tmp", mp3_file)
            
            applescript = f'tell application "Music" to add POSIX file "{mp3_file}" to playlist "{playlist_name}"'
            subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
            print(f"Added: {mp3_file.name}")
        except Exception as e:
            print(f"Error adding {mp3_file.name}: {e}")

def main():
    parser = argparse.ArgumentParser(description='SoundCloud to Apple Music Sync')
    parser.add_argument('--auth-token', required=True)
    parser.add_argument('--playlist-url', required=True)
    parser.add_argument('--album-name', required=True)
    parser.add_argument('--album-artist')
    parser.add_argument('--download-path', required=True)
    
    args = parser.parse_args()
    print("Starting sync process...")
    
    get_apple_music_songs()
    create_playlist(args.album_name)
    success = download_playlist(args.auth_token, args.playlist_url, args.download_path)
    
    if success:
        add_songs_to_apple_music(args.download_path, args.album_name, args.album_artist)
    
    print("Sync complete!")

if __name__ == '__main__':
    main()
