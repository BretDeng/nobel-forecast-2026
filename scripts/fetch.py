"""Read official CLI, following opaque NextOffset; preserve snapshots on failure."""
import argparse, datetime, json, os, subprocess, tempfile, time
from pathlib import Path
from build import ROOT, CATEGORIES
DEFAULT=Path.home()/'Library/Application Support/zhihu-cli/current/zhihu-cli'
def fetch(binary, category, url):
 pages=[]; offset='0'; seen=set()
 for _ in range(100):
  if offset in seen: raise RuntimeError('分页重复，已停止')
  if pages: time.sleep(1)
  seen.add(offset)
  result=subprocess.run([str(binary),'question','answers','--question-url',url,'--limit','50','--offset',offset],capture_output=True,text=True,timeout=60)
  try: page=json.loads(result.stdout)
  except ValueError: raise RuntimeError('CLI 未返回合法 JSON；请检查授权与网络')
  if result.returncode or page.get('Code')!=0:
   message=page.get('Message') or page.get('error',{}).get('message','CLI 请求失败')
   if page.get('Code')==30001 or 'rate limit' in message.lower(): message='知乎暂时限制请求频率或额度，请稍后再同步'
   raise RuntimeError(message)
  paging=page.get('Data',{}).get('Paging',{})
  pages.append(page)
  if paging.get('IsEnd') is True: break
  if paging.get('IsEnd') is not False or paging.get('NextOffset') is None: raise RuntimeError('分页信息不完整，已停止')
  offset=str(paging['NextOffset'])
 else: raise RuntimeError('超出 100 页限制，已停止')
 return {'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pages':pages}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cli',type=Path,default=Path(os.environ.get('ZHIHU_CLI_BINARY',DEFAULT)));args=parser.parse_args()
 if not args.cli.is_file(): raise SystemExit('未找到官方 CLI；请按 README 安装及授权')
 staged={}
 try:
  for index,(key,label,_,qid,_) in enumerate(CATEGORIES):
   if index: time.sleep(1)
   print('读取：'+label,flush=True)
   staged[key]=fetch(args.cli,key,f'https://www.zhihu.com/question/{qid}')
 except (RuntimeError,subprocess.TimeoutExpired) as exc: raise SystemExit('同步失败，保留上次完整快照：'+str(exc))
 # All five must succeed before replacing the previous collection.
 for key,snapshot in staged.items():
  destination=ROOT/f'data/snapshots/{key}.json'
  with tempfile.NamedTemporaryFile(mode='w',dir=destination.parent,delete=False,encoding='utf-8') as f:
   json.dump(snapshot,f,ensure_ascii=False,indent=2);name=f.name
  os.replace(name,destination)
 print('五个问题已同步；新增/变更摘要需要复核。')
if __name__=='__main__':main()
