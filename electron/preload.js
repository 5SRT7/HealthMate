const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('electronAPI', {
  closeApp: () => ipcRenderer.send('close-app'),
  resizeWindow: (w, h) => ipcRenderer.send('resize-window', {width: w, height: h}),
  moveWindow: (dx, dy) => ipcRenderer.send('move-window', {dx, dy}),
});
