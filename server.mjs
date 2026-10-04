import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
const root=fileURLToPath(new URL('.',import.meta.url));
const publicRoot=resolve(root,'public');
const port=Number(process.env.PORT || 2026);
const refreshIntervalMs=2*60*60*1000;
let sync={running:false,success:null,message:'',startedAt:null,finishedAt:null};
let refreshTimer=null;
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
const server=http.createServer(async(req,res)=>{
 if(!['127.0.0.1','localhost'].includes((req.headers.host||'').split(':')[0])){res.writeHead(403);res.end('Invalid host');return;}
 const url=new URL(req.url,'http://127.0.0.1');
 const json=(status,value)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(value));};
 if(url.pathname==='/api/sync') return json(404,{message:'页面不存在'});
 if(req.method!=='GET' && req.method!=='HEAD')return json(405,{message:'不支持此操作'});
 try{
  const path=resolve(publicRoot,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));
  if(!path.startsWith(publicRoot+sep)) return json(403,{message:'禁止访问'});
  const data=await readFile(path);res.writeHead(200,{'Content-Type':types[extname(path)] || 'application/octet-stream','Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:data);
 }catch{return json(404,{message:'页面不存在'});}
});
server.listen(port,'127.0.0.1',()=>console.log(`Nobel Forecast → http://127.0.0.1:${port}`));
function startScheduledRefresh(){
 if(sync.running) return;
 sync={running:true,success:null,message:'正在读取五个知乎问题…',startedAt:new Date().toISOString(),finishedAt:null};
 console.log(`[refresh] ${sync.startedAt} 开始`);
 const child=spawn('python3',['scripts/sync.py'],{cwd:root,stdio:['ignore','pipe','pipe']});
 let error=''; child.stderr.on('data',chunk=>error+=chunk.toString());
 let outputBuffer=''; let resultMessage='';
 child.stdout.on('data',chunk=>{
  outputBuffer+=chunk.toString();
  const lines=outputBuffer.split('\n'); outputBuffer=lines.pop();
  for(const line of lines){
   if(line.startsWith('SYNC_RESULT ')){
    try{resultMessage=JSON.parse(line.slice(12)).message;}catch{}
   }else if(line.trim()){sync.message=line.trim();console.log(`[refresh] ${line.trim()}`);}
  }
 });
 child.on('error',()=>{
  sync={running:false,success:false,message:'无法运行 Python；请检查服务器环境。',startedAt:sync.startedAt,finishedAt:new Date().toISOString()};
  console.error(`[refresh] ${sync.finishedAt} ${sync.message}`);
 });
 child.on('close',code=>{
  const finishedAt=new Date().toISOString();
  if(code!==0){
   sync={running:false,success:false,message:error.trim() || '同步失败；保留已有数据。',startedAt:sync.startedAt,finishedAt};
   console.error(`[refresh] ${finishedAt} ${sync.message}`);
   return;
  }
  sync={running:false,success:true,message:resultMessage || '同步完成；榜单已更新。',startedAt:sync.startedAt,finishedAt};
  console.log(`[refresh] ${finishedAt} ${sync.message}`);
 });
}
refreshTimer=setInterval(startScheduledRefresh,refreshIntervalMs);
refreshTimer.unref();
startScheduledRefresh();
