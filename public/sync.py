#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import ssl
import urllib3
from pathlib import Path

# Fix SSL issues
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except:
    pass

# Use bundled ffmpeg if available via env var set by electron
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', 'ffmpeg')

def find_scdl():
    """Find scdl executable — bundled first, then common system locations"""
    candidates = [
        os.environ.get('SCDL_PATH', ''),  # bundled scdl passed by electron
        os.path.join(os.path.dirname(sys.executable), 'scdl'),
        os.path.expanduser('~/.local/bin/scdl'),
        '/usr/local/bin/scdl',
        '/opt/homebrew/bin/scdl',
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None

def download_playlist(auth_token, playlist_url, download_path):
    """Download SoundCloud playlist using scdl as a subprocess"""
    print("Downloading playlist from SoundCloud...")
    print(f"URL: {playlist_url}")
    print(f"Path: {download_path}")

    os.makedirs(download_path, exist_ok=True)

    scdl_bin = find_scdl()

    # Inject bundled ffmpeg into PATH so scdl can find it automatically
    # scdl does NOT support --ffmpeg-location; it finds ffmpeg via PATH
    env = os.environ.copy()
    env['PATH'] = os.path.dirname(os.path.abspath(FFMPEG_PATH)) + ':' + env.get('PATH', '')

    if scdl_bin:
        print(f"Using scdl at: {scdl_bin}")
        cmd = [
            scdl_bin,
            '-l', playlist_url,
            '--auth-token', auth_token,
            '--path', download_path,
            '--onlymp3',
        ]
    else:
        print("scdl binary not found, trying python module...")
        cmd = [
            sys.executable, '-m', 'scdl',
            '-l', playlist_url,
            '--auth-token', auth_token,
            '--path', download_path,
            '--onlymp3',
        ]

    try:
        result = subprocess.run(cmd, env=env)
        if result.returncode == 0:
            print("Download complete!")
            return True
        else:
            print(f"scdl exited with code {result.returncode}")
            return False
    except Exception as e:
        print(f"Download error: {e}")
        return False

def get_apple_music_songs():
    """Get count of songs in Apple Music library"""
    print("Checking Apple Music library...")
    applescript = 'tell application "Music" to return count of tracks'
    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        count = int(result.stdout.strip())
        print(f"Found {count} songs in Apple Music library")
        return count
    except:
        print("Could not read Apple Music library count")
        return 0

def create_playlist(name):
    """Create a new playlist in Apple Music"""
    print(f"Creating playlist: {name}")
    applescript = f'tell application "Music" to make new playlist with properties {{name:"{name}"}}'
    try:
        subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        print(f"Playlist '{name}' created")
        return True
    except Exception as e:
        print(f"Failed to create playlist: {e}")
        return False

def add_songs_to_apple_music(folder_path, playlist_name, album_artist):
    """Add downloaded mp3s to Apple Music and target playlist"""
    mp3_files = sorted(Path(folder_path).rglob('*.mp3'))
    print(f"Found {len(mp3_files)} files to add")

    if not mp3_files:
        print("No mp3 files found — check your auth token and playlist URL")
        return

    for mp3_file in mp3_files:
        try:
            if album_artist:
                tmp = str(mp3_file) + '.tmp.mp3'
                cmd = [
                    FFMPEG_PATH,
                    '-i', str(mp3_file),
                    '-metadata', f'album_artist={album_artist}',
                    '-c', 'copy',
                    tmp, '-y'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    os.replace(tmp, str(mp3_file))
                elif os.path.exists(tmp):
                    os.remove(tmp)

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
    parser.add_argument('--album-artist', default='')
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