"""Reviewed selections from the 2026-10-04 official CLI summaries.
Indices refer to ordered raw pages; output uses stable answer tokens + summary hashes.
Only explicit positive predictions or explicitly desired nominees count. No keyword voting.
"""
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Each entry: summary index: (canonical people separated by |, normalized directions).
SELECTIONS={
'medicine':{
0:('Jeffrey M. Friedman|Svetlana Mojsov|Daniel Drucker|Jens Juul Holst|Napoleone Ferrara|卢煜明|Lewis C. Cantley|Bert Vogelstein|Robert Weinberg|Karl Deisseroth|Peter Hegemann|Gero Miesenböck|Emmanuel Mignot','GLP-1|瘦素与能量稳态|血管生成与抗 VEGF 疗法|游离 DNA 与无创产前检测|癌症信号与肿瘤生物学|光遗传学|食欲素与睡眠调控'),
1:('Svetlana Mojsov|Jens Juul Holst|Daniel Drucker','GLP-1'),
3:('卢煜明','游离 DNA 与无创产前检测'),
4:('Joel Habener|Svetlana Mojsov|Lotte Bjerre Knudsen','GLP-1'),
6:('','临床医学与药学'),
7:('陈志坚|卢煜明|李文渝|Lotte Bjerre Knudsen|Masashi Yanagisawa','cGAS–STING 与先天免疫|游离 DNA 与无创产前检测|神经退行性疾病|GLP-1|食欲素与睡眠调控'),
8:('Michael N. Hall|森和俊|Peter Walter','mTOR 与细胞生长|未折叠蛋白应答'),
10:('Emmanuel Mignot|Masashi Yanagisawa','食欲素与睡眠调控'),
11:('Svetlana Mojsov|Daniel Drucker|Jens Juul Holst','GLP-1'),
13:('Brian Druker|Anne Dejean|陈竺','白血病靶向与分化治疗'),
14:('小川诚二|卢煜明|Karl Deisseroth|Peter Hegemann|Gero Miesenböck','功能性磁共振成像|游离 DNA 与无创产前检测|光遗传学'),
15:('卢煜明','游离 DNA 与无创产前检测'),
16:('Svetlana Mojsov|Joel Habener|Jens Juul Holst','GLP-1'),
19:('Max D. Cooper|Jacques Miller|Karl Deisseroth|Peter Hegemann|Gero Miesenböck|Wolfram Schultz|Peter Dayan','B 细胞与 T 细胞|光遗传学|多巴胺与奖励机制'),
20:('Daniel Drucker|Jens Juul Holst|Svetlana Mojsov','GLP-1'),
21:('Hans Clevers|Irving Weissman|Hugues de Thé|陈竺','成体干细胞与类器官|白血病靶向与分化治疗'),
22:('陈志坚|刘如谦','cGAS–STING 与先天免疫|精准基因编辑'),
23:('Brian Druker','白血病靶向与分化治疗'),
24:('Karl Deisseroth|Peter Hegemann|Gero Miesenböck|卢煜明','光遗传学|游离 DNA 与无创产前检测'),
25:('Svetlana Mojsov','GLP-1'),
26:('','GLP-1'),
27:('','GLP-1|CAR-T 细胞疗法'),
28:('Timothy Springer','细胞黏附与免疫调控'),
30:('Daniel Drucker|Jens Juul Holst|Svetlana Mojsov','GLP-1'),
32:('Karl Deisseroth|Peter Hegemann|Gero Miesenböck','光遗传学'),
33:('','GLP-1'),35:('','GLP-1'),
36:('Joel Habener|Jens Juul Holst|Daniel Drucker|Svetlana Mojsov','GLP-1'),
},
'physics':{
0:('Jainendra Jain|Moty Heiblum|James Eisenstein','分数量子霍尔与任意子'),
1:('舛冈富士雄|Stuart Parkin|大野英男|Michael Berry|Yakir Aharonov|Bertrand Halperin|香取秀俊|叶军|Pablo Jarillo-Herrero|Allan MacDonald|饭岛澄男|Sajeev John|Eli Yablonovitch|Susumu Noda|佐川真人|David Payne|Emmanuel Desurvire|中泽正隆','存储器与自旋电子学|几何相位与 AB 效应|光晶格原子钟|魔角石墨烯与转角电子学|光子晶体|永磁材料|光纤通信'),
4:('香取秀俊|叶军','光晶格原子钟'),
5:('','复杂系统'),7:('叶军|香取秀俊','光晶格原子钟'),
8:('','金刚石 NV 色心'),
10:('Pablo Jarillo-Herrero|Allan MacDonald|Rafi Bistritzer|Eva Andrei','魔角石墨烯与转角电子学'),
11:('Toshiki Tajima|陈丕燊|Wim Leemans|Yakir Aharonov','等离子体尾场加速|几何相位与 AB 效应'),
14:('Yakir Aharonov|Michael Berry|Tadashi Kadowaki|Hidetoshi Nishimori|Edward Farhi','几何相位与 AB 效应|量子退火计算'),
15:('Michael Berry|Yakir Aharonov','几何相位与 AB 效应'),
16:('薛其坤|John Pendry|David Smith|安达千波矢|Stephen Forrest|Mark Thompson','量子反常霍尔效应|超材料与负折射率|OLED'),
18:('','几何相位与 AB 效应'),
20:('Pablo Jarillo-Herrero|Allan MacDonald|Rafi Bistritzer|Federico Capasso|Susumu Noda|Martin Rees|Roy Kerr|Alessandra Buonanno|Alexei Kitaev|David Deutsch|Charles Bennett','魔角石墨烯与转角电子学|激光器|天体物理学|量子计算'),
21:('Yoshinori Tokura|Hideo Hosono|Jun Akimitsu','超导材料与强关联电子'),
22:('薛其坤|Alexei Kitaev','拓扑物态与量子霍尔|OLED|量子计算'),
23:('Robert Dennard|舛冈富士雄|Stuart Parkin','存储器与自旋电子学'),
24:('舛冈富士雄|中泽正隆','存储器与自旋电子学|光纤通信'),
25:('','魔角石墨烯与转角电子学'),
27:('杨建磊',''),
33:('叶军|Immanuel Bloch','光晶格原子钟|超冷原子量子模拟'),
35:('薛其坤','量子反常霍尔效应'),
36:('Michael Berry','几何相位与 AB 效应'),
37:('杨建磊','超导材料与强关联电子'),
38:('Immanuel Bloch|叶军|香取秀俊','超冷原子量子模拟|光晶格原子钟'),
40:('Yakir Aharonov|Michael Berry|John Pendry|David Smith|Federico Capasso|Andrea Alù|Carlos Frenk','几何相位与 AB 效应|超材料与负折射率|宇宙大尺度结构与冷暗物质'),
42:('Sajeev John|Eli Yablonovitch','光子晶体'),
44:('薛其坤','量子反常霍尔效应'),45:('','地球与空间物理'),
46:('薛其坤','量子反常霍尔效应'),
47:('Alexei Kitaev|Michael Berry','量子计算|几何相位与 AB 效应'),
48:('','等离子体尾场加速|自由电子激光'),49:('邓青云','OLED'),
53:('薛其坤','量子反常霍尔效应'),
55:('香取秀俊|叶军','光晶格原子钟'),56:('叶军','光晶格原子钟'),57:('','天体物理学'),
59:('Christopher Jarzynski','非平衡态热力学'),
62:('','拓扑超导与马约拉纳准粒子'),
},
'chemistry':{
0:('Franz-Ulrich Hartl|Arthur Horwich|森和俊|Peter Walter|Shankar Balasubramanian|David Klenerman|Pascal Mayer|Clifford Brangwynne|Anthony Hyman|Michael Rosen|Craig Crews|Raymond Deshaies|Nathanael Gray|Bonnie Bassler|Peter Greenberg|Jeffrey Gordon|Stephen Buchwald|John Hartwig','蛋白质折叠与未折叠蛋白应答|下一代 DNA 测序|生物分子凝聚体|靶向蛋白降解|细菌群体感应|肠道微生物组|钯催化交叉偶联'),
1:('David Allara|Ralph Nuzzo|Jacob Sagiv','自组装单分子层'),
2:('Roberto Car|Michele Parrinello|Yoshitaka Tanimura|Krzysztof Matyjaszewski|Mitsuo Sawamoto','Car–Parrinello 分子动力学|层级运动方程|可控自由基聚合'),
4:('Peter Schultz|Stuart Schreiber','化学生物学'),
5:('Roberto Car|Michele Parrinello','Car–Parrinello 分子动力学'),
6:('宫坂力','钙钛矿太阳能电池'),
7:('沈建仁|刘如谦','光合作用|精准基因编辑'),
8:('刘如谦|David Allara|Ralph Nuzzo|Jacob Sagiv|Harry Gray|Jay Winkler','精准基因编辑|自组装单分子层|生物电子转移'),
9:('','OLED'),10:('Takeshi Oka',''),11:('','受阻路易斯酸碱对'),
12:('Franz-Ulrich Hartl','蛋白质折叠与未折叠蛋白应答'),
14:('翁启惠',''),
15:('Omar Yaghi|Susumu Kitagawa','金属有机框架（MOF）'),
},
'literature':{
1:('燕妮·埃彭贝克|安妮·卡森',''),
2:('残雪',''),
5:('米歇尔·维勒贝克|安妮·卡森',''),
8:('安妮·卡森|残雪',''),
14:('残雪|玛格丽特·阿特伍德',''),
15:('莉迪亚·若热|米歇尔·德克雷策|燕妮·埃彭贝克|克里斯蒂娜·里韦拉·加尔萨|阿里·史密斯|德博拉·莱维|罗莎·蒙特罗|克里斯蒂娜·佩里·罗西|蕾切尔·卡斯克',''),
16:('安妮·卡森',''),
17:('克里斯蒂娜·里韦拉·加尔萨',''),
18:('安妮·卡森|玛格丽特·阿特伍德',''),
19:('托马斯·品钦',''),
},
'economics':{
0:('John List|Uri Gneezy','实地实验'),
1:('Ernst Fehr|Matthew Rabin','行为经济学'),
2:('Michael Woodford|Jordi Galí|Olivier Blanchard|Steven Berry|James Levinsohn|Ariel Pakes|Elhanan Helpman|Marc Melitz|Charles Manski','新凯恩斯主义与货币政策|实证产业组织与 BLP|国际贸易与企业异质性|部分识别'),
3:('','城市经济学'),
4:('Steven Berry|James Levinsohn|Ariel Pakes|Michael Woodford|Susan Athey|Hal Varian|Gene Grossman|Elhanan Helpman|Marc Melitz|Colin Camerer|George Loewenstein|Matthew Rabin|Ernst Fehr|Thomas Piketty|Emmanuel Saez|Gabriel Zucman','实证产业组织与 BLP|新凯恩斯主义与货币政策|数字经济与信息技术|国际贸易与企业异质性|行为经济学|收入与财富不平等'),
5:('','国际贸易与企业异质性'),
7:('Jonathan Eaton|Samuel Kortum|Marc Melitz','国际贸易与企业异质性|信息经济学与博弈精炼'),
8:('David Autor|Lawrence Katz|Ariel Pakes','劳动经济学与技术变革|实证产业组织与 BLP'),
9:('Susan Athey|Hal Varian','数字经济与信息技术'),
10:('Steven Berry|James Levinsohn|Ariel Pakes','实证产业组织与 BLP'),
11:('Michael Woodford|Susan Athey|Hal Varian|Sidney Winter','新凯恩斯主义与货币政策|数字经济与信息技术'),
12:('Thomas Piketty|Emmanuel Saez|Sendhil Mullainathan|Gabriel Zucman|Raj Chetty','收入与财富不平等'),
13:('Susan Athey|Hal Varian','数字经济与信息技术'),
14:('Richard Blundell',''),15:('林毅夫',''),
17:('Matthew Jackson|Sanjeev Goyal|Yves Zenou|Emir Kamenica|Dirk Bergemann|Stephen Morris','网络经济学|信息设计'),
18:('David Autor|Marc Melitz|Tim Besley|John List',''),
25:('Thomas Piketty|Emmanuel Saez|Gabriel Zucman','收入与财富不平等'),
26:('David Autor|Lawrence Katz','劳动经济学与技术变革'),
27:('Susan Athey|Victor Chernozhukov|Whitney Newey|Tim Besley','因果推断与机器学习|政治经济学'),
28:('David Autor','劳动经济学与技术变革'),
}}
REASONS={
'medicine':{2:'对 GLP-1、食欲素及异种移植持否定预测；其余名单未显示',5:'摘要截断，未显示具体预测',9:'历史回顾，未显示今年预测',12:'通论及历史回顾',17:'跨奖项内容，缺少医学预测',18:'明确表示今年也不会给，不计正向预测',29:'未提出具体候选',31:'明确拒绝预测',34:'语境不明，待核实',37:'仅提背景事件，未明确预测',38:'自荐推销，未明确可辨识候选'},
'physics':{2:'分析授奖趋势，未显示最终选择',3:'未显示明确预测',6:'摘要截断，未显示具体预测',9:'摘要截断，未显示具体预测',12:'内容为神经生物学，奖项不匹配',13:'摘要截断，未显示具体预测',17:'摘要截断，未显示具体方向',19:'评论，无具体预测',26:'讨论评奖方式，无具体预测',28:'明显戏谑表述',29:'摘要截断，未显示具体预测',30:'历史评论',31:'负向清单，不计正向预测',32:'自荐理论，无明确预测',34:'无明确候选或预测',39:'往年预测链接',41:'评论，无具体预测',43:'狗头标记，戏谑名单',50:'转述引文桂冠新闻，无明确本人预测',51:'自荐理论，无明确预测',52:'摘要截断，未显示最终选择',54:'评论，无具体预测',58:'与医学回答重复且奖项不匹配',60:'预测无人获奖，无候选',61:'搞笑诺贝尔奖，非本榜范围',63:'落选理由与背景混合，无法确认正向选择',64:'询问未来年份，不是今年预测'},
'chemistry':{3:'明确表示今年不预测',13:'玩笑，无具体候选'},
'literature':{0:'摘要截断，未显示具体预测',3:'转述赔率榜，未表达本人选择',4:'摘要截断，未显示具体预测',6:'摘要截断，未显示具体预测',7:'转述赔率与历史，未表达本人选择',9:'否定东亚作家，不计正向预测',10:'转述赔率榜，未表达本人选择',11:'调侃 AI，无具体作家',12:'无文学奖预测',13:'戏谑表述',20:'明确表示今年几率不高，不计正向预测'},
'economics':{6:'明确表示不打算猜，转述市场赔率',16:'自荐方案，无可辨识候选',19:'讽刺表述，无具体候选',20:'宽泛趋势，未提出明确成果',21:'戏谑表述',22:'未显示具体研究方向或候选',23:'评论，无具体候选',24:'评论，无具体候选',29:'表情，无预测',30:'否定名单，不计正向预测',31:'语境不明，待核实',32:'明确拒绝预测',33:'语境不明，待核实',34:'戏谑表述'},
}

def main():
 out={}
 for cat, selections in SELECTIONS.items():
  items=[]
  pages=sorted((ROOT/'data/raw').glob(cat+'-*.json'),key=lambda p:int(p.stem.split('-')[-1]))
  for file in pages:
   response=json.loads(file.read_text()); assert response['Code']==0
   items.extend(response['Data']['Items'])
  records={}
  for i,item in enumerate(items):
   assert i in selections or i in REASONS[cat],(cat,i)
   people, directions=selections.get(i,('',''))
   records[item['ContentToken']]={'summaryHash':hashlib.sha256(item['Summary'].encode()).hexdigest(),'reviewed':True,'people':people.split('|') if people else [],'directions':directions.split('|') if directions else [],'reason':REASONS[cat].get(i,'摘要中明确预测或希望获奖；只计可辨识人名，截断名单不补全'),'warnings':[]}
   if cat=='chemistry' and i==15:
    records[item['ContentToken']]['warnings']=['该回答将已获 2025 化学奖的 MOF 再预测为 2026。保留原始预测，标记事实错误。']
   if cat=='medicine' and i==22:
    records[item['ContentToken']]['warnings']=['刘如谦：回答更看好化学奖，但在本医学问题中也列为候选。']
  out[cat]=records
 (ROOT/'data/reviews.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print('Reviewed',sum(len(v) for v in out.values()),'summaries.')
if __name__=='__main__': main()
