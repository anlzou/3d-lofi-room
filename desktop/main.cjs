const {app,BrowserWindow,protocol}=require('electron');
const fs=require('node:fs/promises');
const path=require('node:path');
protocol.registerSchemesAsPrivileged([{scheme:'room',privileges:{standard:true,secure:true,supportFetchAPI:true,stream:true}}]);
const smoke=process.argv.includes('--smoke-test');
let rendererErrors=0;
app.whenReady().then(async()=>{
  const root=path.resolve(__dirname,'../dist');
  protocol.handle('room',async request=>{
    const url=new URL(request.url);
    if(url.hostname!=='home')return new Response('',{status:403});
    let file;
    try{file=path.resolve(root,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));}catch{return new Response('',{status:400});}
    if(!file.startsWith(root+path.sep))return new Response('',{status:403});
    const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.glb':'model/gltf-binary','.wasm':'application/wasm','.wav':'audio/wav','.json':'application/json'};
    try{return new Response(await fs.readFile(file),{headers:{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Content-Security-Policy':"default-src 'self'; script-src 'self' 'wasm-unsafe-eval' blob:; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; media-src 'self' blob:; connect-src 'self' blob:; object-src 'none'; base-uri 'none'"}});}catch{return new Response('',{status:404});}
  });
  const win=new BrowserWindow({width:1280,height:900,minWidth:720,minHeight:600,show:!smoke,title:'3d-lofi-room · 四季房间',backgroundColor:'#252a30',autoHideMenuBar:true,webPreferences:{contextIsolation:true,nodeIntegration:false,sandbox:true}});
  win.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  win.webContents.on('will-navigate',(e,url)=>{if(!url.startsWith('room://home/'))e.preventDefault();});
  win.webContents.session.setPermissionRequestHandler((_wc,_permission,callback)=>callback(false));
  win.webContents.on('console-message',(_event,...args)=>{if(args[0]===3)rendererErrors++;if(smoke)console.log('RENDERER',...args);});
  await win.loadURL('room://home/');
  if(smoke){
    const started=Date.now();let checking=false;
    const timer=setInterval(async()=>{
      if(checking)return;checking=true;
      const status=await win.webContents.executeJavaScript('document.querySelector("#status")?.textContent');
      if(status?.includes('已就绪')){
        clearInterval(timer);await fs.mkdir(path.join(process.cwd(),'release-check'),{recursive:true});
        win.showInactive();
        await new Promise(resolve=>setTimeout(resolve,1000));
        const audioBytes=await win.webContents.executeJavaScript('fetch("audio/window-seat.wav").then(r=>{if(!r.ok)throw Error("Audio missing");return r.arrayBuffer()}).then(b=>b.byteLength)');
        if(audioBytes<1000000)throw new Error('Packaged music is incomplete');
        await fs.writeFile(path.join(process.cwd(),'release-check/desktop.png'),(await win.webContents.capturePage()).toPNG());
        console.log(rendererErrors?'DESKTOP_SMOKE_FAILED':'DESKTOP_SMOKE_OK',status,'audio bytes',audioBytes,'errors',rendererErrors);app.exit(rendererErrors?1:0);
      }else if(Date.now()-started>45000){clearInterval(timer);console.error('DESKTOP_SMOKE_FAILED',status);app.exit(1);}else checking=false;
    },500);
  }
});
app.on('window-all-closed',()=>app.quit());

