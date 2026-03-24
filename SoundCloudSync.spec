# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['hello/main.py'],  # your actual python entry point
    pathex=['/Users/miguelvera/Desktop/soundcloud-sync-app'],
    binaries=[],
    datas=[('README.md', '.'), ('assets/*', 'assets')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SoundCloudSync',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.icns',
)

app = BUNDLE(
    exe,
    name='SoundCloudSync.app',
    icon='icon.icns',
    bundle_identifier='com.miguel.soundcloudsync',
)
