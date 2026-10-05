import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from review import validate,parse_response,canonicalize,catalog_for

class ZhidaReviewTests(unittest.TestCase):
 def source(self,text):return {'ContentToken':'9001','Summary':text}
 def item(self,status='include',people=None,directions=None):return {'id':'9001','status':status,'people':people or [],'directions':directions or [],'reason':'明确的预测或排除判断'}
 def test_explicit_vote_with_original_evidence(self):
  text='我押Daniel J. Drucker，方向是GLP-1。'
  item=self.item(people=[{'name':'Daniel Drucker','evidence':text}],directions=[{'name':'GLP-1','evidence':text}])
  result=validate(item,self.source(text),{'people':{'Daniel Drucker':['Daniel Drucker','Daniel J. Drucker']},'directions':{'GLP-1':['GLP-1']}})
  self.assertEqual(result['people'],['Daniel Drucker']);self.assertEqual(result['directions'],['GLP-1']);self.assertEqual(result['reviewMethod'],'zhida')
 def test_hallucinated_quote_rejected(self):
  item=self.item(people=[{'name':'Hans Clevers','evidence':'我押Hans Clevers'}])
  with self.assertRaises(ValueError):validate(item,self.source('我押GLP-1。'),{'people':{},'directions':{}})
 def test_original_quote_cannot_support_unmentioned_candidate(self):
  item=self.item(people=[{'name':'Hans Clevers','evidence':'我押GLP-1。'}])
  with self.assertRaises(ValueError):validate(item,self.source('我押GLP-1。'),{'people':{},'directions':{}})
 def test_excluded_mentions_never_receive_votes(self):
  item=self.item(status='exclude',directions=[{'name':'GLP-1','evidence':'我觉得GLP-1今年不会给'}])
  result=validate(item,self.source('我觉得GLP-1今年不会给'),{'people':{},'directions':{}})
  self.assertTrue(result['reviewed']);self.assertEqual(result['directions'],[])
 def test_uncertain_never_receive_votes(self):
  result=validate(self.item(status='uncertain'),self.source('背景分析…'),{'people':{},'directions':{}})
  self.assertFalse(result['reviewed']);self.assertEqual(result['people'],[])
 def test_wrong_answer_id_rejected(self):
  item=self.item(status='exclude');item['id']='other'
  with self.assertRaises(ValueError):validate(item,self.source('背景'),{'people':{},'directions':{}})
 def test_aliases_do_not_split_existing_candidates(self):
  self.assertEqual(canonicalize('Dennis Lo','我预测Dennis Lo',{'卢煜明':['卢煜明','Dennis Lo']}),'卢煜明')
 def test_mojsov_chinese_quote_supports_existing_candidate(self):
  catalogs={'people':catalog_for({'medicine':{'a':{'people':['Svetlana Mojsov']}}},'medicine','people'),'directions':{}}
  text='获奖人选：斯维特兰娜·莫伊索'
  result=validate(self.item(people=[{'name':'Svetlana Mojsov','evidence':text}]),self.source(text),catalogs,'medicine')
  self.assertEqual(result['people'],['Svetlana Mojsov'])
 def test_malformed_output_rejected(self):
  with self.assertRaises(ValueError):parse_response({'choices':[{'message':{'content':'我预测三个人。'}}]})
 def test_protocol_parsed_without_extraneous_prose(self):
  trial={'choices':[{'message':{'content':json.dumps({'items':[self.item(status='exclude')]})}}]}
  self.assertEqual(parse_response(trial)[0]['status'],'exclude')
 def test_literature_directions_rejected(self):
  item=self.item(directions=[{'name':'先锋文学','evidence':'我押先锋文学'}])
  with self.assertRaises(ValueError):validate(item,self.source('我押先锋文学'),{'people':{},'directions':{}},'literature')
 def test_cached_uncertain_and_human_reviews_do_not_call_ai(self):
  import tempfile,hashlib,review
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'data/snapshots').mkdir(parents=True)
   text='不确定';digest=hashlib.sha256(text.encode()).hexdigest()
   reviews={'literature':{'9001':{'summaryHash':digest,'reviewed':False,'reviewMethod':'zhida','people':[],'directions':[]},'9002':{'summaryHash':digest,'reviewed':True,'people':[],'directions':[]}}}
   (root/'data/reviews.json').write_text(json.dumps(reviews))
   (root/'data/snapshots/literature.json').write_text(json.dumps({'pages':[{'Data':{'Items':[{'ContentToken':'9001','Summary':text},{'ContentToken':'9002','Summary':text}]}}]}))
   with patch.object(review,'ROOT',root),patch.object(review,'CATEGORIES',[('literature','文学','','1','L')]),patch('review.subprocess.run') as run:
    result=review.review_pending(Path('/cli'))
    run.assert_not_called();self.assertEqual(result['calls'],0)
if __name__=='__main__':unittest.main()
