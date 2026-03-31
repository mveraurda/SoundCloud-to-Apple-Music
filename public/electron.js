const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const express = require('express');
const fs = require('fs');
const os = require('os');
 
let mainWindow;
let expressApp;
 
function getResourcesPath() {
    if (process.resourcesPath) return process.resourcesPath;
    return path.join(__dirname, '..', 'resources');
}
 
function getSyncBinPath() { return path.join(getResourcesPath(), 'sync_bin'); }
function getSpotifyBinPath() { return path.join(getResourcesPath(), 'sync_spotify_bin'); }
function getFfmpegPath() { return path.join(getResourcesPath(), 'ffmpeg'); }
 
function ensureBinariesExecutable() {
    [getSyncBinPath(), getSpotifyBinPath(), getFfmpegPath()].forEach(bin => {
        try { if (fs.existsSync(bin)) fs.chmodSync(bin, '755'); } catch(e) {}
    });
}
 
function createServer() {
    expressApp = express();
    expressApp.use(express.json());
    expressApp.use(express.static(path.join(__dirname, '.')));
 
    const CONFIG_FILE = path.join(os.homedir(), '.soundcloud_sync', 'config.txt');
 
    expressApp.post('/api/config/save', (req, res) => {
        const { authToken, playlistUrl, albumName, albumArtist, downloadPath, spPlaylistUrl, spDownloadPath } = req.body;
        const dir = path.dirname(CONFIG_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
 
        const configContent = `AUTH_TOKEN=${authToken || ''}
PLAYLIST_URL=${playlistUrl || ''}
DOWNLOAD_PATH=${downloadPath || ''}
ALBUM_NAME=${albumName || ''}
ALBUM_ARTIST=${albumArtist || ''}
SP_PLAYLIST_URL=${spPlaylistUrl || ''}
SP_DOWNLOAD_PATH=${spDownloadPath || ''}`;
 
        fs.writeFileSync(CONFIG_FILE, configContent);
        res.json({ success: true });
    });
 
    expressApp.get('/api/config/get', (req, res) => {
        try {
            if (fs.existsSync(CONFIG_FILE)) {
                const content = fs.readFileSync(CONFIG_FILE, 'utf8');
                const config = {};
                content.split('\n').forEach(line => {
                    const [key, ...rest] = line.split('=');
                    const value = rest.join('=');
                    if (key && value !== undefined) config[key.toLowerCase()] = value.trim();
                });
                res.json(config);
            } else {
                res.json({});
            }
        } catch(err) { res.json({}); }
    });
 
    // APPLE MUSIC SYNC
    expressApp.post('/api/sync/start', (req, res) => {
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
 
        const { authToken, playlistUrl, downloadPath } = req.body;
        const syncBin = getSyncBinPath();
        const ffmpegPath = getFfmpegPath();
 
        if (!fs.existsSync(syncBin)) {
            res.write(`data: ${JSON.stringify({ type: 'error', message: 'Sync binary not found. Please reinstall the app.' })}\n\n`);
            res.end();
            return;
        }
 
        const env = { ...process.env, FFMPEG_PATH: ffmpegPath, PATH: `${getResourcesPath()}:${process.env.PATH}` };
 
        const proc = spawn(syncBin, [
            '--auth-token', authToken,
            '--playlist-url', playlistUrl,
            '--download-path', downloadPath
        ], { env });
 
        proc.stdout.on('data', data => {
            data.toString().split('\n').forEach(line => {
                if (line.trim()) res.write(`data: ${JSON.stringify({ type: 'log', message: line })}\n\n`);
            });
        });
        proc.stderr.on('data', data => {
            data.toString().split('\n').forEach(line => {
                if (line.trim()) res.write(`data: ${JSON.stringify({ type: 'log', message: line })}\n\n`);
            });
        });
        proc.on('close', code => {
            if (code !== 0) res.write(`data: ${JSON.stringify({ type: 'error', message: `Process exited with code ${code}` })}\n\n`);
            else res.write(`data: ${JSON.stringify({ type: 'complete', message: 'Sync complete!' })}\n\n`);
            res.end();
        });
        proc.on('error', err => {
            res.write(`data: ${JSON.stringify({ type: 'error', message: `Failed to start sync: ${err.message}` })}\n\n`);
            res.end();
        });
    });
 
    // SPOTIFY SYNC
    expressApp.post('/api/sync/spotify', (req, res) => {
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
 
        const { authToken, playlistUrl, downloadPath } = req.body;
        const spotifyBin = getSpotifyBinPath();
        const ffmpegPath = getFfmpegPath();
 
        if (!fs.existsSync(spotifyBin)) {
            res.write(`data: ${JSON.stringify({ type: 'error', message: 'Spotify sync binary not found. Please reinstall the app.' })}\n\n`);
            res.end();
            return;
        }
 
        const env = { ...process.env, FFMPEG_PATH: ffmpegPath, PATH: `${getResourcesPath()}:${process.env.PATH}` };
 
        const proc = spawn(spotifyBin, [
            '--auth-token', authToken,
            '--playlist-url', playlistUrl,
            '--download-path', downloadPath
        ], { env });
 
        proc.stdout.on('data', data => {
            data.toString().split('\n').forEach(line => {
                if (line.trim()) res.write(`data: ${JSON.stringify({ type: 'log', message: line })}\n\n`);
            });
        });
        proc.stderr.on('data', data => {
            data.toString().split('\n').forEach(line => {
                if (line.trim()) res.write(`data: ${JSON.stringify({ type: 'log', message: line })}\n\n`);
            });
        });
        proc.on('close', code => {
            if (code !== 0) res.write(`data: ${JSON.stringify({ type: 'error', message: `Process exited with code ${code}` })}\n\n`);
            else res.write(`data: ${JSON.stringify({ type: 'complete', message: 'Sync complete!' })}\n\n`);
            res.end();
        });
        proc.on('error', err => {
            res.write(`data: ${JSON.stringify({ type: 'error', message: `Failed to start sync: ${err.message}` })}\n\n`);
            res.end();
        });
    });
 
    expressApp.get('/health', (req, res) => res.json({ status: 'ok' }));
 
    return expressApp.listen(3001, () => console.log('Server running on http://localhost:3001'));
}
 
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400, height: 900, minWidth: 1200, minHeight: 700,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        }
    });
    mainWindow.loadURL(`file://${path.join(__dirname, 'index.html')}`);
    mainWindow.on('closed', () => { mainWindow = null; });
}
 
ipcMain.handle('select-directory', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory', 'createDirectory'],
        defaultPath: path.join(os.homedir(), 'Music')
    });
    if (!result.canceled && result.filePaths.length > 0) return result.filePaths[0];
    return null;
});

ipcMain.handle('open-folder', async (event, folderPath) => {
    try {
        const { shell } = require('electron');
        await shell.openPath(folderPath);
        return { success: true };
    } catch (e) {
        return { success: false, error: e.message };
    }
});
 
app.on('ready', () => {
    ensureBinariesExecutable();
    createServer();
    createWindow();
 
    const template = [
        {
            label: 'SoundCloud Sync',
            submenu: [
                {
                    label: 'About',
                    click: () => dialog.showMessageBox(mainWindow, {
                        type: 'info',
                        title: 'SoundCloud Sync',
                        message: 'SoundCloud Sync',
                        detail: 'Download SoundCloud playlists to Apple Music or Spotify\n\nVersion 1.3.0'
                    })
                },
                { type: 'separator' },
                { label: 'Quit', accelerator: 'Cmd+Q', click: () => app.quit() }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' }, { role: 'redo' }, { type: 'separator' },
                { role: 'cut' }, { role: 'copy' }, { role: 'paste' }
            ]
        }
    ];
 
    Menu.setApplicationMenu(Menu.buildFromTemplate(template));
});
 
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (mainWindow === null) createWindow(); });
process.on('exit', () => {});