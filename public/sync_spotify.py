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

def open_spotify():
    print("Opening Spotify...")
    try:
        subprocess.run(['open', '-a', 'Spotify'], capture_output=True)
        print("Spotify opened — check Local Files for your songs.")
    except Exception as e:
        print(f"Could not open Spotify: {e}")

def main():
    parser = argparse.ArgumentParser(description='SoundCloud to Spotify Sync')
    parser.add_argument('--auth-token', required=True)
    parser.add_argument('--playlist-url', required=True)
    parser.add_argument('--download-path', required=True)

    args = parser.parse_args()
    print("Starting Spotify sync...")

    success = download_playlist(args.auth_token, args.playlist_url, args.download_path)

    if success:
        open_spotify()
        print(f"Songs downloaded to: {args.download_path}")
        print("In Spotify go to Settings, then Local Files, and add this folder as a source.")

    print("Sync complete!")

if __name__ == '__main__':
    main()
