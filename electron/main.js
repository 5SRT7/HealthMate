const { app, BrowserWindow, ipcMain, Tray, Menu, nativeImage } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let mainWindow = null, tray = null, backend = null;
const URL = 'http://localhost:8000';

function startBackend() {
  const dir = path.join(__dirname, '..');
  backend = spawn('uv', ['run', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'], {cwd: dir, stdio: ['ignore', 'pipe', 'pipe']});
  backend.stdout.on('data', d => process.stdout.write(d));
  backend.stderr.on('data', d => process.stderr.write(d));
  backend.on('exit', c => {if (c!==0) console.log('Backend exit:', c)});
}

function waitForBackend(n=60) {
  return new Promise((res, rej) => {
    const ck = t => {
      if (t<=0) return rej(new Error('Backend not ready'));
      http.get(URL+'/api/v1/health', r => r.statusCode===200 ? res() : setTimeout(()=>ck(t-1),1000)).on('error', ()=>setTimeout(()=>ck(t-1),1000));
    }; ck(n);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 180, height: 120,
    frame: false, transparent: true,
    alwaysOnTop: true, hasShadow: false, resizable: false,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), nodeIntegration: false, contextIsolation: true },
  });
  mainWindow.loadURL(URL+'?_t='+Date.now()).catch(e => console.error('Load fail:', e.message));
  mainWindow.webContents.on('did-fail-load', (ev, code) => {
    if (code===-102) mainWindow.loadURL('data:text/html,'+encodeURIComponent('<body style="display:flex;align-items:center;justify-content:center;height:100vh;background:#0f111f;color:rgba(255,255,255,.5);font-family:sans-serif;font-size:11px;border-radius:16px;"><p>后端未启动</p></body>'));
  });
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon); tray.setToolTip('HealthMate');
  tray.setContextMenu(Menu.buildFromTemplate([
    {label:'显示/隐藏', click:()=>mainWindow.isVisible()?mainWindow.hide():mainWindow.show()},
    {type:'separator'},
    {label:'退出', click:()=>{app.isQuitting=true;app.quit()}},
  ]));
  tray.on('click', ()=>mainWindow.isVisible()?mainWindow.hide():mainWindow.show());
  mainWindow.on('close', e => {if (!app.isQuitting){e.preventDefault();mainWindow.hide()}});
}

ipcMain.on('close-app', ()=>{app.isQuitting=true;app.quit()});
ipcMain.on('resize-window', (e, {width, height}) => { if (mainWindow) mainWindow.setSize(width, height); });

app.whenReady().then(async () => {
  startBackend();
  try { await waitForBackend(); console.log('Backend ready'); } catch(e) { console.error('Backend fail:', e.message); }
  createWindow();
});
app.on('window-all-closed', ()=>{if(backend)backend.kill();if(process.platform!=='darwin')app.quit()});
app.on('before-quit', ()=>{if(backend)backend.kill()});
