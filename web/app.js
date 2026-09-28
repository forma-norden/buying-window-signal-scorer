const $ = id => document.getElementById(id);
let settings = null, profiles = {}, keyReady = false, capManual = false, activeProfile = 'growth';
const markets = {us:'United States',uk:'United Kingdom',ca:'Canada',au:'Australia',in:'India',de:'Germany',fr:'France',sg:'Singapore',za:'South Africa'};
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const safeLink = url => /^https?:\/\//i.test(url || '') ? escapeHtml(url) : '#';
const lines = id => $(id).value.split('\n').map(x => x.trim()).filter(Boolean);
const fill = (id, items) => { $(id).value = (items || []).join('\n'); };
const message = (text, error=false) => { $('message').textContent = text; $('message').classList.toggle('error', error); };
const api = async (path, options={}) => { const response = await fetch(path, {headers:{'Content-Type':'application/json'}, ...options}); const body = await response.json(); if(!response.ok) throw new Error(body.detail || 'Request failed'); return body; };
function showSettings(config){
  settings = structuredClone(config);
  $('profile-name').value=config.profile_name; $('news-query').value=config.news_query;
  fill('role-queries',config.role_queries);fill('strong-roles',config.roles.strong);fill('adjacent-roles',config.roles.adjacent);fill('mandate-terms',config.mandate_terms);
  $('event-groups').value=Object.entries(config.events).map(([name,terms])=>`${name}: ${terms.join(', ')}`).join('\n');
  $('market-label').value=config.locations[0].label;$('market-gl').value=config.locations[0].gl;
  for(const [key,value] of Object.entries(config.weights)) $('weight-'+key).value=value;
  $('max-accounts').value=config.max_accounts;$('max-requests').value=config.max_requests;
  activeProfile=Object.entries(profiles).find(([,value])=>value.profile_name===config.profile_name)?.[0] || 'custom';
  document.querySelectorAll('.profile-card').forEach(card=>card.setAttribute('aria-pressed',String(card.dataset.profile===activeProfile)));
  const fields=['role_queries','roles','mandate_terms','news_query','events','weights'];
  const customised=activeProfile==='custom'||fields.some(field=>JSON.stringify(config[field])!==JSON.stringify(profiles[activeProfile][field]));
  $('profile-state').textContent=customised?'Customised profile':'';
  $('profile-state').hidden=!customised;
  $('market').value=markets[config.locations[0].gl]===config.locations[0].label?config.locations[0].gl:'custom';
  $('scan-size').value=[3,6,12].includes(config.max_accounts)?String(config.max_accounts):'custom';
}
function readSettings(){
  const events={};
  for(const line of lines('event-groups')){
    const colon=line.indexOf(':');if(colon<1)throw new Error('Write each news group as label: phrase, phrase');
    const label=line.slice(0,colon).trim();if(events[label])throw new Error('News group labels must be unique');
    events[label]=line.slice(colon+1).split(',').map(x=>x.trim()).filter(Boolean);
  }
  return {...settings,profile_name:$('profile-name').value.trim(),news_query:$('news-query').value.trim(),role_queries:lines('role-queries'),roles:{strong:lines('strong-roles'),adjacent:lines('adjacent-roles')},mandate_terms:lines('mandate-terms'),events,locations:[{label:$('market-label').value.trim(),gl:$('market-gl').value.trim().toLowerCase()}],weights:Object.fromEntries(['role','recency','news','convergence'].map(key=>[key,Number($('weight-'+key).value)])),max_accounts:Number($('max-accounts').value),max_requests:Number($('max-requests').value)};
}
function mode(){return document.querySelector('input[name="mode"]:checked').value;}
function autoCap(){
  if(capManual)return;
  const accounts=$('watchlist').value.split('\n').map(x=>x.split('|')[0].trim().toLowerCase()).filter(Boolean);
  const planned=mode()==='watchlist'?new Set(accounts).size*2:lines('role-queries').length+Number($('max-accounts').value);
  $('max-requests').value=Math.min(150,Math.max(4,planned+4,Math.ceil(planned*1.25)));
}
async function preflight(){
  $('watchlist-wrap').hidden=mode()!=='watchlist';
  $('scan-size-wrap').hidden=mode()==='watchlist';
  autoCap();
  try{const e=await api('/api/estimate',{method:'POST',body:JSON.stringify({mode:mode(),watchlist:$('watchlist').value,settings:readSettings()})});$('preflight').textContent=`At most ${e.planned_upper_bound} searches: ${e.jobs_requests} jobs + ${e.news_requests_upper_bound} news. Limit: ${e.attempt_cap} API attempts including retries.`;$('preflight').classList.toggle('warning',!e.within_cap);$('run').disabled=!e.within_cap || !keyReady;}
  catch(err){$('preflight').textContent=err.message;$('preflight').classList.add('warning');$('run').disabled=true;}
}
function evidence(items, kind, newIds=[]){
  if(!items.length)return '<p class="muted">No matching evidence in this scan.</p>';
  return `<ul class="evidence">${items.map(x=>`<li><a href="${safeLink(x.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(x.title)}</a>${newIds.includes(x.id)?'<span class="new-badge"> FIRST SEEN IN SCAN</span>':''}<small>${escapeHtml(kind==='job'?x.company+' · '+(x.posted_at||'Date unknown'):x.event+' · '+(x.date||'Date unknown')+' · '+(x.source||'Source unknown'))}${kind==='news'?' · match '+escapeHtml(x.identity_confidence):''}</small>${kind==='job'&&x.mandate_evidence?.length?`<blockquote>${escapeHtml(x.mandate_evidence[0])}</blockquote>`:''}</li>`).join('')}</ul>`;
}
function render(report, scroll=true){
  if(!report)return;
  $('results-section').hidden=false;
  document.querySelector('.export').hidden=!!report.demo;
  $('run-summary').textContent=`${report.profile_name} · ${report.account_count} companies · ${report.job_count} relevant jobs · ${report.request_count} searches · ${new Date(report.scanned_at).toLocaleString()}${report.demo?' · FICTIONAL SAMPLE':''}`;
  $('caveat').classList.toggle('partial',report.partial);
  $('caveat').hidden=!report.partial&&!report.demo;
  $('caveat').textContent=report.partial?`${report.errors.length} request(s) failed. Results are partial.`:'Fictional sample data';
  $('accounts').innerHTML=report.accounts.length?report.accounts.map((row,index)=>`<details class="account" ${index===0?'open':''}><summary><div class="score">${row.score}<small>/ 100</small></div><div><h3>${escapeHtml(row.company)}</h3><div class="account-sub">${row.jobs.length} job(s) · ${row.news.length} news item(s)${report.comparison==='repeat'?` · ${(row.first_seen_jobs?.length||0)+(row.first_seen_news?.length||0)} first seen`:''}${row.review_flags?.length?' · review flagged':''}</div></div><span class="expand-icon" aria-hidden="true"></span></summary><div class="account-body">${row.review_flags?.length?`<div class="review-flags">${row.review_flags.map(escapeHtml).join(' · ')}</div>`:''}<div class="parts">${Object.entries(row.parts).map(([name,value])=>`<span>${escapeHtml(name)} ${value}/${report.weights[name]}</span>`).join('')}</div><h4>Hiring evidence</h4>${evidence(row.jobs,'job',row.first_seen_jobs)}<h4>News evidence</h4>${evidence(row.news,'news',row.first_seen_news)}</div></details>`).join(''):'<div class="empty">No matching companies in this scan. Try a broader role phrase or a watchlist.</div>';
  if(scroll)$('results-section').scrollIntoView({behavior:'smooth',block:'start'});
}
async function doRun(path,body){
  $('run').disabled=true;$('demo').disabled=true;message(path.endsWith('scan')?'Searching jobs and news. This may take a few minutes…':'Loading fictional sample…');
  try{const result=await api(path,{method:'POST',body:JSON.stringify(body)});render(result.report);message(result.report.partial?'Scan finished with partial results. Review the notice above.':result.report.demo?'Growth sample loaded.':'Scan complete. Open a company to inspect the evidence.');}
  catch(err){message(err.message,true);}finally{$('demo').disabled=false;await preflight();}
}
document.addEventListener('DOMContentLoaded',async()=>{
  try{const [info,presetInfo]=await Promise.all([api('/api/config'),api('/api/profiles')]);profiles=presetInfo.profiles;keyReady=info.key_ready;showSettings(info.config);$('key-status').textContent=keyReady?'KEY READY':'ADD API KEY';$('key-status').classList.toggle('missing',!keyReady);document.querySelector('.setup-instruction').hidden=keyReady;await preflight();const prior=await api('/api/latest');if(prior.report)render(prior.report,false);}catch(err){message(err.message,true);}
  document.querySelectorAll('.profile-card').forEach(card=>card.addEventListener('click',()=>{const next=structuredClone(profiles[card.dataset.profile]);next.locations=[{label:$('market-label').value,gl:$('market-gl').value}];next.max_accounts=Number($('max-accounts').value);next.max_requests=Number($('max-requests').value);showSettings(next);preflight();}));
  $('market').addEventListener('change',()=>{if($('market').value==='custom'){$('editor').open=true;document.querySelectorAll('.editor-group')[2].open=true;$('market-label').focus();return;}$('market-label').value=markets[$('market').value];$('market-gl').value=$('market').value;preflight();});
  $('scan-size').addEventListener('change',()=>{if($('scan-size').value==='custom'){$('editor').open=true;document.querySelectorAll('.editor-group')[2].open=true;$('max-accounts').focus();return;}$('max-accounts').value=$('scan-size').value;preflight();});
  document.querySelectorAll('input[name="mode"]').forEach(input=>input.addEventListener('change',preflight));
  document.querySelectorAll('#editor input,#editor textarea,#watchlist').forEach(input=>input.addEventListener('input',()=>{if(input.id==='max-requests')capManual=true;if(input.id==='max-accounts')$('scan-size').value='custom';if(input.id==='market-label'||input.id==='market-gl')$('market').value='custom';if(input.id!=='watchlist'){$('profile-state').textContent='Customised profile';$('profile-state').hidden=false;}clearTimeout(window.preflightTimer);window.preflightTimer=setTimeout(preflight,250);}));
  $('demo').addEventListener('click',()=>doRun('/api/demo',{}));
  $('run').addEventListener('click',()=>{try{doRun('/api/scan',{mode:mode(),watchlist:$('watchlist').value,settings:readSettings()});}catch(err){message(err.message,true);}});
});
