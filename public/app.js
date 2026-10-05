const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data, state={cat:'medicine',mode:'people',page:'leader',search:'',excludeAi:false,ascending:false,expanded:null,audit:'all'};
let displayed=[];
const dateFormat=new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Hong_Kong',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
const current=()=>data.categories.find(c=>c.id===state.cat);
const isFrozen=cat=>Boolean(cat.predictionFreezeAt)&&Date.now()>=Date.parse(cat.predictionFreezeAt);
const freezeNote=cat=>cat.predictionFreezeAt?`${isFrozen(cat)?'已封榜 · 数据不再更新':'最后更新截止'}：${dateFormat.format(new Date(cat.predictionFreezeAt))}（香港时间）`:'';
function countdownState(cat,now=Date.now()){
 const freeze=Date.parse(cat.predictionFreezeAt),announcement=Date.parse(cat.announcementAt);
 if(!Number.isFinite(freeze)||!Number.isFinite(announcement))return null;
 const phase=now<freeze?'open':now<announcement?'frozen':'announcement';
 const remaining=Math.max(0,Math.ceil(((phase==='open'?freeze:announcement)-now)/1000));
 return {phase,remaining,days:Math.floor(remaining/86400),hours:Math.floor(remaining%86400/3600),minutes:Math.floor(remaining%3600/60),seconds:remaining%60};
}
function updateCountdown(){
 const clock=countdownState(current());if(!clock)return;
 const panel=$('#award-countdown');panel.dataset.phase=clock.phase;
 panel.classList.toggle('closing-soon',clock.phase==='open'&&clock.remaining<=3600);
 $('#countdown-status').textContent=clock.phase==='open'?'预测进行中':clock.phase==='frozen'?'已封榜':'揭晓时间已到';
 $('#countdown-label').textContent=clock.phase==='open'?'距预测封榜':clock.phase==='frozen'?'距官方开奖':'预测已定格';
 $('#countdown-clock').hidden=clock.phase==='announcement';
 $('#countdown-clock').setAttribute('aria-label',clock.phase==='open'?'距预测封榜的剩余时间':'距官方开奖的剩余时间');
 $('#countdown-finished').hidden=clock.phase!=='announcement';
 for(const unit of ['days','hours','minutes','seconds'])$(`[data-countdown="${unit}"]`).textContent=String(clock[unit]).padStart(2,'0');
}
function renderCountdown(){
 const cat=current(),panel=$('#award-countdown');panel.hidden=!countdownState(cat);if(panel.hidden)return;
 panel.innerHTML=`<div class="countdown-main"><div class="countdown-heading"><span id="countdown-label"></span><span class="countdown-status" id="countdown-status"></span></div><div class="countdown-clock" id="countdown-clock" role="timer" aria-live="off" aria-label="距截止的剩余时间">${[['days','天'],['hours','时'],['minutes','分'],['seconds','秒']].map(([unit,label])=>`<span class="countdown-part"><strong data-countdown="${unit}">00</strong><small>${label}</small></span>`).join('')}</div><p class="countdown-finished" id="countdown-finished" hidden>等电话响，等名字揭晓。</p></div><div class="countdown-schedule"><div><span>预测封榜</span><time datetime="${esc(cat.predictionFreezeAt)}">${esc(dateFormat.format(new Date(cat.predictionFreezeAt)))}</time></div><div><span>开奖时间</span><time datetime="${esc(cat.announcementAt)}">${esc(dateFormat.format(new Date(cat.announcementAt)))}</time></div><p>香港时间 UTC+8 · 开奖前 1 小时封榜<br>开奖按官方最早揭晓时间 · <a href="${esc(cat.announcementSource)}" target="_blank" rel="noopener noreferrer">官方日程 ↗</a></p></div>`;
 updateCountdown();
}
const filteredAnswers=()=>current().answers.filter(a=>!(state.excludeAi&&a.aiAssisted));
const validAnswers=()=>filteredAnswers().filter(a=>a.people.length||a.directions.length);
function toast(message){$('#toast').textContent=message;$('#toast').style.display='block';clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').style.display='none',3500);}
function rowsFor(kind){
 const cat=current(), answers=filteredAnswers();
 const rows=cat[kind].map(row=>({...row,sourceIds:row.sourceIds.filter(id=>answers.some(a=>a.id===id))})).map(r=>({...r,count:r.sourceIds.length})).filter(r=>r.count);
 rows.sort((a,b)=>b.count-a.count||a.name.localeCompare(b.name,'zh-CN'));
 let prev=-1,rank=0;
 rows.forEach((r,i)=>{if(r.count!==prev)rank=i+1;r.rank=rank;prev=r.count;});
 return rows;
}
function renderStats(){
 const total=data.categories.reduce((s,c)=>s+c.total,0), valid=data.categories.reduce((s,c)=>s+c.valid,0);
 const last=data.categories.reduce((a,c)=>new Date(c.fetchedAt)>new Date(a)?c.fetchedAt:a,data.categories[0].fetchedAt);
 $('#stats').innerHTML=`<div class="stat"><div class="stat-label">覆盖奖项 <span>↗</span></div><div class="stat-value">05<small>个奖项</small></div><div class="stat-caption">医学 · 物理 · 化学 · 文学 · 经济学</div></div><div class="stat"><div class="stat-label">已获取回答摘要</div><div class="stat-value">${total}<small>条</small></div><div class="stat-caption">${data.categories.every(c=>c.complete)?'已遍历接口返回的全部分页':'部分分页尚未完成'}</div></div><div class="stat"><div class="stat-label">有效预测回答</div><div class="stat-value">${valid}<small>条</small></div><div class="stat-caption">逐条复核 · 每项预测每回答最多一票</div></div><div class="stat"><div class="stat-label">最近采集时间 <span class="live-dot"></span></div><div class="stat-value time">${esc(dateFormat.format(new Date(last)))}</div><div class="stat-caption">2026 年 · 香港时间 UTC+8</div></div>`;
}
function sourceCard(a){return `<div class="source-card"><div class="source-card-head"><span>回答 <small>${esc(a.id)}</small></span><a href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">查看原回答 ↗</a></div><p>${esc(a.summary)}</p><div class="source-tags"><span>${a.reviewMethod==='zhida'?'知乎直答 AI 复核':'人工复核'}</span>${a.aiAssisted?'<span class="ai-tag">明确 AI 辅助</span>':''}${a.people.length?`<span>${a.people.length} 位候选人</span>`:''}${a.directions.length?`<span>${a.directions.length} 个归类方向</span>`:''}</div>${a.warnings.map(w=>`<p class="warning-note">${esc(w)} ${w.includes("2025")?`<a href="${esc(data.factCheckUrl)}" target="_blank" rel="noopener noreferrer">核查来源 ↗</a>`:""}</p>`).join('')}</div>`;}
function renderTable(){
 const rows=rowsFor(state.mode);let shown=rows.filter(r=>`${r.name} ${r.english}`.toLowerCase().includes(state.search.toLowerCase()));
 if(state.ascending)shown=shown.toReversed();displayed=shown;
 const denom=validAnswers().length;
 $('#result-meta').textContent=`${shown.length} ${state.mode==='people'?'位候选人':'个方向'} · ${denom} 条有效预测回答`;
 if(!shown.length){$('#table-container').innerHTML='<div class="empty">没有匹配的预测<p>试试其他名字，或清除搜索条件。</p></div>';return;}
 $('#table-container').innerHTML=`<table class="leader-table"><thead><tr><th>排名</th><th>${state.mode==='people'?'候选人 / CANDIDATE':'成果方向 / FIELD'}</th><th><button id="sort-count" aria-label="按预测票数${state.ascending?'降序':'升序'}排序">预测票数 ${state.ascending?'↑':'↓'}</button></th><th>样本占比</th><th>来源</th></tr></thead><tbody>${shown.map(r=>{
 const percentage=denom?r.count/denom*100:0;
 const selectedSources=filteredAnswers().filter(a=>r.sourceIds.includes(a.id));
 const warning=selectedSources.some(a=>a.warnings.length);
 return `<tr class="${r.rank===1?'first':''}"><td class="${r.rank<=3?'top-rank':''}">${String(r.rank).padStart(2,'0')}</td><td><span class="candidate-name">${esc(r.name)}${warning?'<span class="warning">有核查提示</span>':''}</span><span class="candidate-sub">${esc(r.english|| (state.mode==='people'?'候选人 · 摘要中的明确预测':'研究方向 · 规范化归类'))}</span></td><td class="count">${r.count}</td><td class="share-cell"><div class="share"><div class="bar-track"><span style="width:${percentage}%"></span></div><span>${percentage.toFixed(1)}%</span></div></td><td><button class="source-button" data-source="${r.id}" aria-expanded="${state.expanded===r.id}" aria-label="${esc(r.name)}，展开 ${r.count} 条预测来源">${state.expanded===r.id?'−':'+'}</button></td></tr>${state.expanded===r.id?`<tr class="source-row"><td colspan="5"><div class="sources"><div class="sources-heading"><span>${r.count} 条预测依据 · 服务端摘要</span><span>每条回答计 1 票</span></div>${selectedSources.map(sourceCard).join('')}</div></td></tr>`:''}`;
 }).join('')}</tbody></table>`;
}
function renderAudit(){
 const all=current().answers;
 const rows=all.filter(a=>state.audit==='all'||(state.audit==='positive'&&(a.people.length||a.directions.length))||(state.audit==='excluded'&&a.reviewed&&!a.people.length&&!a.directions.length)||(state.audit==='pending'&&!a.reviewed)).filter(a=>`${a.summary} ${a.reason} ${a.id}`.toLowerCase().includes(state.search.toLowerCase()));
 $('#result-meta').textContent=`${rows.length} / ${all.length} 条摘要 · 原始来源与复核结果`;
 $('#table-container').innerHTML=`<div class="audit-heading"><span>回答复核记录</span><select id="audit-filter" aria-label="筛选复核状态"><option value="all">全部摘要</option><option value="positive">纳入统计</option><option value="excluded">不计正向票</option><option value="pending">待人工复核</option></select></div>${rows.length?rows.map(a=>`<article class="audit-card"><div class="source-card-head"><span class="status ${!a.reviewed?'pending':!a.people.length&&!a.directions.length?'excluded':''}">${!a.reviewed?'待人工复核':a.people.length||a.directions.length?'纳入统计':'不计正向票'}${a.reviewMethod==='zhida'?' · 直答 AI':''}</span><a href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">回答 ${esc(a.id.slice(-6))} ↗</a></div><p>${esc(a.summary)}</p><div class="review-reason">${esc(a.reason)}${a.people.length?`<br>候选人：${esc(a.people.join('、'))}`:''}${a.directions.length?`<br>归类方向：${esc(a.directions.join('、'))}`:''}</div>${a.warnings.map(w=>`<p class="warning-note">${esc(w)} ${w.includes("2025")?`<a href="${esc(data.factCheckUrl)}" target="_blank" rel="noopener noreferrer">核查来源 ↗</a>`:""}</p>`).join('')}</article>`).join(''):'<div class="empty">没有匹配的摘要</div>'}`;
 $('#audit-filter').value=state.audit;
}
function renderInsights(){
 const cat=current(),directions=rowsFor('directions'),people=rowsFor('people');
 const top=cat.id==='literature'?people[0]:directions[0];
 $('#insights').innerHTML=`<div class="aside-label">AT A GLANCE / 榜单观察</div><div class="insight-top"><div class="top-label">${cat.id==='literature'?'Most anticipated author':'Most anticipated field'}</div><h3>${esc(top?.name||'暂无复核结果')}</h3><p>${cat.id==='literature'?'目前样本中最被期待的作家。文学奖以作家为统计单位，作品不单独计票。':'目前样本中被最多回答预测的成果方向。人选组合存在差异，方向归类后合并计票。'}</p><div class="insight-value">${top?.count??0}<small>条回答${top&&((cat.id==='literature'?people:directions).filter(r=>r.count===top.count).length>1)?' · 并列首位':''}</small></div></div><div class="sample"><h4>本奖项样本覆盖</h4><div class="sample-bar" aria-hidden="true"><span style="width:${cat.valid/cat.total*100}%"></span><span class="pending" style="width:${cat.pending/cat.total*100}%"></span></div><div class="sample-row"><span>获取摘要</span><strong>${cat.total}</strong></div><div class="sample-row"><span>有效预测</span><strong>${cat.valid}</strong></div><div class="sample-row"><span>不计正向票</span><strong>${cat.excluded}</strong></div><div class="sample-row"><span>待人工复核</span><strong>${cat.pending}</strong></div><div class="sample-row"><span>独立用户人数</span><strong>无法确认</strong></div></div><div class="reading"><h4>如何读这张榜？</h4><p>一条回答可以预测多个候选。候选与方向分别统计，首选和备选都计入。点击行末的 ＋，查看支持这一预测的原始摘要。</p><p>采集：${esc(dateFormat.format(new Date(cat.fetchedAt)))}<br>${cat.complete?'接口分页已全部读取':'接口分页尚未完成'} · 数据为摘要<br>${esc(freezeNote(cat))}</p><button id="aside-method">查看完整统计方法 ↗</button></div>`;
}
function render(){
 const cat=current();
 $('#categories').innerHTML=data.categories.map(c=>`<button class="category-tab" role="tab" aria-selected="${c.id===state.cat}" data-category="${c.id}"><span class="tab-symbol">${c.symbol}</span>${c.label}<small>${c.total}</small></button>`).join('');
 $('#category-en').textContent=cat.english+' / 2026';
 $('#board-title').textContent=cat.label+(state.page==='audit'?' · 数据与来源':'奖预测榜');
 $('#question-link').href=cat.questionUrl;
 renderCountdown();
 $('#leader-nav').classList.toggle('active',state.page==='leader');$('#audit-nav').classList.toggle('active',state.page==='audit');
 $('#people-mode').classList.toggle('selected',state.mode==='people');$('#directions-mode').classList.toggle('selected',state.mode==='directions');
 $('#directions-mode').disabled=cat.id==='literature';
 $('.segmented').style.display=state.page==='audit'?'none':'flex';
 $('#exclude-ai').closest('label').style.display=state.page==='audit'?'none':'flex';
 $('#search').placeholder=state.page==='audit'?'搜索摘要或复核理由…':state.mode==='people'?'搜索候选人…':'搜索成果方向…';
 $('#search').value=state.search;
 $('.table-foot').style.display=state.page==='audit'?'none':'flex';
 if(state.page==='audit')renderAudit();else renderTable();renderInsights();
 history.replaceState(null,'',`#${state.cat}/${state.page}/${state.mode}`);
}
function method(){if(!$('#method-dialog').open)$('#method-dialog').showModal();}
function exportCsv(){
 const denom=validAnswers().length;
 const quote=v=>'"'+String(v).replaceAll('"','""')+'"';
 const rows=[['排名',state.mode==='people'?'候选人':'方向','英文名','独立回答票数','有效预测回答样本占比','来源链接','统计单位','奖项','采集时间'],...displayed.map(r=>[r.rank,r.name,r.english,r.count,(r.count/denom*100).toFixed(1)+'%',current().answers.filter(a=>r.sourceIds.includes(a.id)).map(a=>a.url).join(' '),'answer（无法确认用户人数）',current().label,current().fetchedAt])];
 const blob=new Blob(['\uFEFF'+rows.map(r=>r.map(quote).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`nobel-2026-${state.cat}-${state.mode}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);toast('已导出当前筛选结果');
}
async function loadData(){const r=await fetch('./data.json');if(!r.ok)throw Error('读取榜单数据失败');data=await r.json();}
document.addEventListener('click',event=>{
 const button=event.target.closest('button');if(!button)return;
 if(button.dataset.category){state.cat=button.dataset.category;state.search='';state.expanded=null;state.ascending=false;if(state.cat==='literature')state.mode='people';render();}
 else if(button.dataset.source){state.expanded=state.expanded===button.dataset.source?null:button.dataset.source;renderTable();}
 else if(['method-nav','scope-method','aside-method'].includes(button.id))method();
 else if(button.id==='close-method')$('#method-dialog').close();
 else if(button.id==='people-mode'||button.id==='directions-mode'){state.mode=button.id==='people-mode'?'people':'directions';state.search='';state.expanded=null;render();}
 else if(button.id==='leader-nav'||button.id==='audit-nav'){state.page=button.id==='leader-nav'?'leader':'audit';state.search='';state.expanded=null;render();// Finish navigation immediately so its animation cannot compete with wheel scrolling.
 $('.board').scrollIntoView({behavior:'instant',block:'start'});}
 else if(button.id==='sort-count'){state.ascending=!state.ascending;renderTable();}
 else if(button.id==='export-button')exportCsv();
});
$('#search').addEventListener('input',e=>{state.search=e.target.value;state.page==='audit'?renderAudit():renderTable();});
document.addEventListener('change',e=>{if(e.target.id==='exclude-ai'){state.excludeAi=e.target.checked;state.expanded=null;render();}if(e.target.id==='audit-filter'){state.audit=e.target.value;renderAudit();}});
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!$('#method-dialog').open){e.preventDefault();$('#search').focus();}});
$('#method-dialog').addEventListener('click',e=>{if(e.target===$('#method-dialog')){const rect=e.target.getBoundingClientRect();if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)e.target.close();}});
try{
 await loadData();const [cat,page,mode]=location.hash.slice(1).split('/');if(data.categories.some(c=>c.id===cat))state.cat=cat;if(page==='audit')state.page=page;if(mode==='directions'&&state.cat!=='literature')state.mode=mode;
 renderStats();render();setInterval(updateCountdown,1000);setInterval(()=>{renderInsights();},30000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateCountdown();});$('#method-list').innerHTML=data.methodology.map(s=>`<li>${esc(s)}</li>`).join('');
}catch(e){$('#table-container').innerHTML=`<div class="empty">${esc(e.message)}<p>请运行 npm run build 后刷新。</p></div>`;}
