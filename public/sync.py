#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import ssl
import urllib3
from pathlib import Path

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except:
    pass

FFMPEG_PATH = os.environ.get('FFMPEG_PATH', 'ffmpeg')

def download_playlist(auth_token, playlist_url, download_path):
    print("Downloading playlist from SoundCloud...")
    print(f"URL: {playlist_url}")
    print(f"Path: {download_path}")

    os.makedirs(download_path, exist_ok=True)

    ffmpeg_dir = os.path.dirname(os.path.abspath(FFMPEG_PATH))
    env = os.environ.copy()
    env['PATH'] = ffmpeg_dir + ':' + env.get('PATH', '')
    os.environ.update(env)

    try:
        import scdl.scdl as scdl_module
        sys.argv = [
            'scdl',
            '-l', playlist_url,
            '--auth-token', auth_token,
            '--path', download_path,
            '--onlymp3',
            '--yt-dlp-args', f'--ffmpeg-location {FFMPEG_PATH}'
        ]
        print("Calling scdl directly...")
        scdl_module._main()
        print("Download complete!")
        return True
    except SystemExit as e:
        if e.code == 0 or str(e) == '0':
            print("Download complete!")
            return True
        print(f"scdl exited: {e}")
        return False
    except Exception as e:
        print(f"Download error: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_apple_music_count():
    print("Checking Apple Music library...")
    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell application "Music" to return count of tracks'],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip())
        print(f"Found {count} songs in Apple Music library")
        return count
    except:
        print("Could not read Apple Music library count")
        return 0

def add_songs_to_apple_music(folder_path):
    mp3_files = sorted(Path(folder_path).rglob('*.mp3'))
    print(f"Found {len(mp3_files)} files to add")

    if not mp3_files:
        print("No mp3 files found — check your auth token and playlist URL")
        return

    for mp3_file in mp3_files:
        try:
            applescript = f'tell application "Music" to add POSIX file "{mp3_file}"'
            subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
            print(f"Added: {mp3_file.name}")
        except Exception as e:
            print(f"Error adding {mp3_file.name}: {e}")

def main():
    parser = argparse.ArgumentParser(description='SoundCloud to Apple Music Sync')
    parser.add_argument('--auth-token', required=True)
    parser.add_argument('--playlist-url', required=True)
    parser.add_argument('--download-path', required=True)

    args = parser.parse_args()
    print("Starting sync process...")

    get_apple_music_count()
    success = download_playlist(args.auth_token, args.playlist_url, args.download_path)

    if success:
        add_songs_to_apple_music(args.download_path)

    print("Sync complete!")

if __name__ == '__main__':
    main()