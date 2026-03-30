const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    selectDirectory: () => ipcRenderer.invoke('select-directory'),
    openFolder: (folderPath) => ipcRenderer.invoke('open-folder', folderPath)
});