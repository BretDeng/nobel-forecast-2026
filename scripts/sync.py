"""User-triggered fetch → Zhida review → deterministic leaderboard build."""
import argparse,json,os,time
from pathlib import Path
from build import ROOT,main as build
from fetch import DEFAULT,sync_fetch
from review import review_pending
from deadlines import cutoff,utc_now
from datetime import timedelta

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--final-category',choices=['medicine','physics','chemistry','literature','economics']);args=parser.parse_args()
 selected=None
 if args.final_category:
  selected={args.final_category}
  target=cutoff(args.final_category)-timedelta(seconds=30)
  while utc_now()<target:
   remaining=(target-utc_now()).total_seconds()
   if remaining>20*60:raise SystemExit('最后更新任务只能在截止前 20 分钟内运行。')
   print(f'等待最后采集：{args.final_category}，剩余 {int(remaining)} 秒',flush=True)
   time.sleep(min(remaining,30))
 binary=Path(os.environ.get('ZHIHU_CLI_BINARY',DEFAULT))
 updated=sync_fetch(binary,selected)
 if not updated:
  if args.final_category:raise SystemExit('最后更新错过截止或采集越过截止；保留之前快照，不补采封榜后的数据。')
  print('SYNC_RESULT '+json.dumps({'message':'没有可更新奖项；封榜快照保持不变。','pending':0,'reviewed':0,'aiCalls':0},ensure_ascii=False),flush=True)
  return
 review=review_pending(binary,category_ids=updated)
 build()
 data=json.loads((ROOT/'public/data.json').read_text())
 pending=sum(c['pending'] for c in data['categories'])
 if review['error']:message=f'数据已同步；直答复核暂未完成，{pending} 条需人工复核。'
 elif pending:message=f'同步完成；直答 AI 已处理新增/变更摘要，{pending} 条不确定内容待人工复核。'
 elif review['calls']:message=f'同步完成；直答 AI 已复核 {review["reviewed"]} 条新增/变更摘要，榜单已更新。'
 else:message='同步完成；没有需要新增复核的摘要，榜单已更新。'
 print('SYNC_RESULT '+json.dumps({'message':message,'pending':pending,'reviewed':review['reviewed'],'aiCalls':review['calls']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
