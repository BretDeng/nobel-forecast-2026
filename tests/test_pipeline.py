import hashlib,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build import aggregate,ROOT
from fetch import fetch
from unittest.mock import patch
from types import SimpleNamespace

class PipelineTests(unittest.TestCase):
 def test_duplicate_name_counts_once_and_ties_competition_rank(self):
  records=[{'id':'1','people':['A','A','B'],'aiAssisted':False,'warnings':[]},{'id':'2','people':['C'],'aiAssisted':True,'warnings':[]}]
  rows=aggregate(records,'people')
  self.assertEqual([r['count'] for r in rows],[1,1,1])
  self.assertEqual([r['rank'] for r in rows],[1,1,1])
 def test_competition_ranks(self):
  records=[{'id':str(i),'people':p,'aiAssisted':False,'warnings':[]} for i,p in enumerate([['A','B','C'],['A','B']])]
  self.assertEqual([r['rank'] for r in aggregate(records,'people')],[1,1,3])
 def test_snapshot_all_reviewed_and_counts_match_sources(self):
  output=json.loads((ROOT/'public/data.json').read_text())
  self.assertEqual(len(output['categories']),5)
  self.assertGreater(sum(c['total'] for c in output['categories']),0)
  for category in output['categories']:
   self.assertTrue(category['complete'])
   self.assertEqual(category['valid']+category['excluded']+category['pending'],category['total'])
   self.assertEqual(category['total'],len({a['id'] for a in category['answers']}))
   answers={a['id']:a for a in category['answers']}
   for kind in ['people','directions']:
    for row in category[kind]:
     self.assertEqual(row['count'],len(set(row['sourceIds'])))
     for token in row['sourceIds']:self.assertIn(row['name'],answers[token][kind])
 def test_negative_and_contextual_mentions_not_votes(self):
  output=json.loads((ROOT/'public/data.json').read_text())
  medicine=output['categories'][0]
  rejected={a['id']:a for a in medicine['answers']}
  self.assertEqual(rejected['2087287949775918336']['directions'],[])
  self.assertEqual(rejected['2086038511082287783']['directions'],['成体干细胞与类器官','白血病靶向与分化治疗'])
 def test_empty_page_uses_server_offset(self):
  pages=[{'Code':0,'Data':{'Items':[],'Paging':{'IsEnd':False,'NextOffset':37}}},{'Code':0,'Data':{'Items':[],'Paging':{'IsEnd':True}}}]
  with patch('fetch.subprocess.run',side_effect=[SimpleNamespace(returncode=0,stdout=json.dumps(p)) for p in pages]) as call:
   result=fetch(Path('/cli'),'medicine','https://www.zhihu.com/question/1')
   self.assertEqual(call.call_args_list[1].args[0][-1],'37')
   self.assertEqual(len(result['pages']),2)
 def test_incomplete_paging_stops(self):
  response=SimpleNamespace(returncode=0,stdout=json.dumps({'Code':0,'Data':{'Items':[],'Paging':{'IsEnd':False}}}))
  with patch('fetch.subprocess.run',return_value=response):
   with self.assertRaisesRegex(RuntimeError,'分页信息不完整'):fetch(Path('/cli'),'medicine','https://www.zhihu.com/question/1')
 def test_hash_change_requires_review(self):
  import build,tempfile
  from unittest.mock import patch
  # Exercise the production hash gate with an actual altered source summary.
  with tempfile.TemporaryDirectory() as d:
   tmp=Path(d);(tmp/'data/snapshots').mkdir(parents=True);(tmp/'public').mkdir()
   for file in (ROOT/'data/snapshots').glob('*.json'):(tmp/'data/snapshots'/file.name).write_bytes(file.read_bytes())
   (tmp/'data/reviews.json').write_bytes((ROOT/'data/reviews.json').read_bytes())
   path=tmp/'data/snapshots/medicine.json';snapshot=json.loads(path.read_text());snapshot['pages'][0]['Data']['Items'][0]['Summary']+=' changed';path.write_text(json.dumps(snapshot))
   with patch.object(build,'ROOT',tmp):build.main()
   result=json.loads((tmp/'public/data.json').read_text())['categories'][0]
   self.assertEqual(result['pending'],1)
   self.assertFalse(result['answers'][0]['reviewed'])
   self.assertEqual(result['answers'][0]['people'],[])
if __name__=='__main__':unittest.main()
