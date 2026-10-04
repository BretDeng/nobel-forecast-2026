"""Build a reproducible leaderboard from hash-matched, reviewed summaries."""
import json, hashlib
from pathlib import Path
from collections import defaultdict
from deadlines import metadata
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES=[('medicine','生理学或医学','PHYSIOLOGY OR MEDICINE','2081709250993303561','M'),('physics','物理学','PHYSICS','2081708619905745132','P'),('chemistry','化学','CHEMISTRY','2081709501913248924','C'),('literature','文学','LITERATURE','2085781961016960614','L'),('economics','经济学','ECONOMIC SCIENCES','2084054769849611542','E')]
ENGLISH={'卢煜明':'Dennis Lo','叶军':'Jun Ye','香取秀俊':'Hidetoshi Katori','薛其坤':'Xue Qikun','刘如谦':'David R. Liu','陈志坚':'Zhijian Chen','李文渝':'Virginia Man-Yee Lee','森和俊':'Kazutoshi Mori','残雪':'Can Xue','安妮·卡森':'Anne Carson','燕妮·埃彭贝克':'Jenny Erpenbeck','玛格丽特·阿特伍德':'Margaret Atwood','米歇尔·维勒贝克':'Michel Houellebecq','托马斯·品钦':'Thomas Pynchon','克里斯蒂娜·里韦拉·加尔萨':'Cristina Rivera Garza','陈竺':'Zhu Chen','邓青云':'Ching W. Tang','宫坂力':'Tsutomu Miyasaka','沈建仁':'Jian-Ren Shen','舛冈富士雄':'Fujio Masuoka','中泽正隆':'Masataka Nakazawa','小川诚二':'Seiji Ogawa','翁启惠':'Chi-Huey Wong'}

def aggregate(records,kind):
 buckets=defaultdict(list)
 for r in records:
  for name in set(r[kind]): buckets[name].append(r)
 ordered=sorted(buckets,key=lambda n:(-len(buckets[n]),n.casefold()))
 out=[]; prev=None; rank=0
 for i,name in enumerate(ordered):
  sources=buckets[name]; count=len(sources)
  if count!=prev: rank=i+1
  prev=count
  out.append({'id':hashlib.sha256((kind+name).encode()).hexdigest()[:12],'rank':rank,'name':name,'english':ENGLISH.get(name,''),'count':count,'sourceIds':[r['id'] for r in sources],'aiCount':sum(r['aiAssisted'] for r in sources),'warnings':list(dict.fromkeys(w for r in sources for w in r['warnings']))})
 return out

def main():
 reviews=json.loads((ROOT/'data/reviews.json').read_text())
 categories=[]
 for key,label,eng,qid,symbol in CATEGORIES:
  snapshot=json.loads((ROOT/f'data/snapshots/{key}.json').read_text())
  unique={}
  for page in snapshot['pages']:
   assert page['Code']==0
   for item in page['Data']['Items']:
    unique[str(item['ContentToken'])]=item
  records=[]
  for token,item in unique.items():
   review=reviews.get(key,{}).get(token,{})
   matched=review.get('summaryHash')==hashlib.sha256(item['Summary'].encode()).hexdigest()
   reviewed=bool(matched and review.get('reviewed'))
   record={'id':token,'url':item['Url'],'summary':item['Summary'],'people':review.get('people',[]) if reviewed else [],'directions':review.get('directions',[]) if reviewed else [],'reason':review.get('reason','待复核：新增或摘要有变更') if matched else '待复核：新增或摘要有变更','reviewed':reviewed,'reviewMethod':review.get('reviewMethod','human') if matched else None,'reviewModel':review.get('model') if matched else None,'reviewEvidence':review.get('evidence',[]) if reviewed else [],'aiAssisted':any(s in item['Summary'].lower() for s in ['chatgpt','豆包']),'warnings':review.get('warnings',[]) if reviewed else []}
   records.append(record)
  valid=[r for r in records if r['people'] or r['directions']]
  categories.append({'id':key,'label':label,'english':eng,'symbol':symbol,'questionUrl':f'https://www.zhihu.com/question/{qid}','fetchedAt':snapshot['fetchedAt'],'complete':snapshot['pages'][-1]['Data']['Paging'].get('IsEnd') is True,'total':len(records),'valid':len(valid),'pending':sum(not r['reviewed'] for r in records),'excluded':sum(r['reviewed'] and not r['people'] and not r['directions'] for r in records),'people':aggregate(records,'people'),'directions':aggregate(records,'directions'),'answers':records})
 payload={'year':2026,'countUnit':'answer','authorIdentityAvailable':False,'categories':categories,'methodology':['仅统计指定五个问题，由官方 Zhihu CLI 返回的回答摘要。服务端过滤项、图片及摘要截断部分无法覆盖。','只计摘要中明确预测、备选或明确希望获奖的候选；多选均计一次，不区分首选和备选。','以回答 ContentToken 去重；同一回答重复提名只计一次。接口没有作者标识，无法确认独立用户人数。','初始样本由人工逐条筛选；同步后的新增/变更摘要使用知乎直答 AI 复核，并校验逐字原文依据。无法确定或校验失败的内容留待人工复核；规范化中英文人名及方向。方向可能依据候选人的明确研究领域归类，不反推缺失的人名。','否定预测、纯历史回顾、仅转述赔率、明确玩笑、奖项不匹配和无法辨识的摘要不进入正向榜单。','AI 辅助回答默认纳入；仅在摘要明确提到 ChatGPT 或豆包时标记，未提及不代表完全没有使用 AI。','票数相同并列排名。占比为预测该项的回答 / 当前筛选下的有效回答；多选使占比总和可能超过 100%。','热度是样本中的讨论共识，不代表获奖概率、官方提名或科学成果质量。新增或变更摘要通过直答复核与程序校验后计票，未通过的仍不计票。'],'factCheckUrl':'https://www.nobelprize.org/uploads/2025/10/press-chemistryprize2025.pdf'}
 for category in categories:category.update(metadata(category['id']))
 payload['methodology'].append('各奖项按官方公布的最早揭晓时间提前一小时封榜。截止后停止采集及后续复核；若最后任务迟到或采集越过截止，保留此前快照。最后一次截止前采集的复核和发布可能稍后完成。')
 (ROOT/'public/data.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
 print('Built:',sum(c['total'] for c in categories),'summaries;',sum(c['valid'] for c in categories),'positive prediction answers')
 for c in categories: print(c['label'], c['total'], c['valid'], 'leader:', c['people'][0]['name'] if c['people'] else 'none')
if __name__=='__main__':main()
