"""User-triggered fetch → Zhida review → deterministic leaderboard build."""
import json,os,subprocess,sys
from pathlib import Path
from build import ROOT,main as build
from fetch import DEFAULT
from review import review_pending

def main():
 result=subprocess.run([sys.executable,str(ROOT/'scripts/fetch.py')],cwd=ROOT)
 if result.returncode:raise SystemExit(result.returncode)
 review=review_pending(Path(os.environ.get('ZHIHU_CLI_BINARY',DEFAULT)))
 build()
 data=json.loads((ROOT/'public/data.json').read_text())
 pending=sum(c['pending'] for c in data['categories'])
 if review['error']:message=f'数据已同步；直答复核暂未完成，{pending} 条需人工复核。'
 elif pending:message=f'同步完成；直答 AI 已处理新增/变更摘要，{pending} 条不确定内容待人工复核。'
 elif review['calls']:message=f'同步完成；直答 AI 已复核 {review["reviewed"]} 条新增/变更摘要，榜单已更新。'
 else:message='同步完成；没有需要新增复核的摘要，榜单已更新。'
 print('SYNC_RESULT '+json.dumps({'message':message,'pending':pending,'reviewed':review['reviewed'],'aiCalls':review['calls']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
