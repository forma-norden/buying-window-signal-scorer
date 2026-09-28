const $ = id => document.getElementById(id);
let settings = null;
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const safeLink = url => /^https?:\/\//i.test(url || '') ? escapeHtml(url) : '#';
const lines = id => $(id).value.split('\n').map(x => x.trim()).filter(Boolean);
const fill = (id, items) => { $(id).value = (items || []).join('\n'); };
const message = (text, error=false) => { $('message').textContent = text; $('message').classList.toggle('error', error); };
const api = async (path, options={}) => { const response = await fetch(path, {headers:{'Content-Type':'application/json'}, ...options}); const body = await response.json(); if(!response.ok) throw new Error(body.detail || 'Request failed'); return body; };

function showSettings(config){
  settings = config;
  fill('role-queries', config.role_queries); fill('strong-roles', config.roles.strong); fill('adjacent-roles', config.roles.adjacent);
  fill('mandate-terms', config.mandate_terms);
  fill('funding-terms', config.events.funding); fill('leadership-terms', config.events.leadership);
  for(const [key,value] of Object.entries(config.weights)) $('weight-'+key).value=value;
  $('max-accounts').value=config.max_accounts;
}
function readSettings(){
  return {...settings, role_queries:lines('role-queries'), roles:{...settings.roles,strong:lines('strong-roles'),adjacent:lines('adjacent-roles')},mandate_terms:lines('mandate-terms'),events:{...settings.events,funding:lines('funding-terms'),leadership:lines('leadership-terms')},weights:Object.fromEntries(['role','recency','news','convergence'].map(key=>[key,Number($('weight-'+key).value)])),max_accounts:Number($('max-accounts').value)};
}
function mode(){return document.querySelector('input[name="mode"]:checked').value;}
async function preflight(){
  $('watchlist-wrap').hidden=mode()!=='watchlist';
  try{const e=await api('/api/estimate',{method:'POST',body:JSON.stringify({mode:mode(),watchlist:$('watchlist').value})});$('preflight').textContent=`At most ${e.planned_upper_bound} initial searches: ${e.jobs_requests} jobs + ${e.news_requests_upper_bound} news. Hard limit: ${e.attempt_cap} HTTP attempts including retries.`;$('preflight').classList.toggle('warning',!e.within_cap);$('run').disabled=!e.within_cap;}
  catch(err){$('preflight').textContent=err.message;$('preflight').classList.add('warning');$('run').disabled=true;}
}
function evidence(items, kind){
  if(!items.length) return '<p class="muted">No matching evidence in this scan.</p>';
  return `<ul class="evidence">${items.map(x=>`<li><a href="${safeLink(x.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(x.title)}</a><small>${escapeHtml(kind==='job'?x.company + ' · ' + (x.posted_at || 'Date unknown'):x.event + ' · ' + (x.date || 'Date unknown'))}${kind==='news' ? ' · match confidence: '+escapeHtml(x.identity_confidence) : ''}</small>${kind==='job' && x.mandate_evidence?.length?`<blockquote>${escapeHtml(x.mandate_evidence[0])}</blockquote>`:''}</li>`).join('')}</ul>`;
}
function render(report){
  if(!report)return;
  $('results-section').hidden=false;
  const stamp=new Date(report.scanned_at).toLocaleString();
  $('run-summary').textContent=`${report.account_count} accounts · ${report.job_count} relevant job listings · ${report.request_count} API requests · ${stamp}${report.demo?' · DEMO DATA':''}`;
  $('caveat').classList.toggle('partial',report.partial);
  $('caveat').textContent=report.partial ? `${report.errors.length} request(s) failed. This is a partial scan; inspect the errors before acting. ${report.method}` : (report.demo?'Labelled fixture, not a live market result. ':'')+report.method;
  $('accounts').innerHTML=report.accounts.length ? report.accounts.map((row,index)=>`<details class="account" ${index===0?'open':''}><summary><div class="score">${row.score}<small>/ 100</small></div><div><h3>${escapeHtml(row.company)}</h3><div class="account-sub">${row.jobs.length} relevant job(s) · ${row.news.length} candidate news hit(s) · identity ${escapeHtml(row.identity_confidence)} · ICP ${escapeHtml(row.icp_fit)}${row.review_flags?.length?' · review flagged':''}</div></div><span class="chevron" aria-hidden="true">⌄</span></summary><div class="account-body"><p>${escapeHtml(row.explanation)}</p>${row.review_flags?.length?`<div class="review-flags">${row.review_flags.map(escapeHtml).join(' · ')}</div>`:''}<div class="parts">${Object.entries(row.parts).map(([name,value])=>`<span>${escapeHtml(name)} ${value}/${report.weights[name]}</span>`).join('')}</div><h4>Hiring evidence</h4>${evidence(row.jobs,'job')}<h4>News evidence</h4>${evidence(row.news,'news')}</div></details>`).join('') : '<div class="empty">No matching accounts in this scan. Try broader role phrases or a different watchlist.</div>';
  $('results-section').scrollIntoView({behavior:'smooth',block:'start'});
}
async function doRun(path, body){
  $('run').disabled=true;$('demo').disabled=true;message(path.endsWith('scan')?'Scanning jobs and news. This may take a few minutes…':'Loading labelled demo…');
  try{const result=await api(path,{method:'POST',body:JSON.stringify(body)});render(result.report);message(result.report.partial?'Scan finished with partial results. Review the warning above.':'Scan complete. Open an account to inspect its evidence.');}
  catch(err){message(err.message,true);}finally{$('demo').disabled=false;await preflight();}
}
document.addEventListener('DOMContentLoaded',async()=>{
  try{const info=await api('/api/config');showSettings(info.config);$('key-status').textContent=info.key_ready?'API KEY READY':'DEMO ONLY';$('key-status').classList.toggle('missing',!info.key_ready);await preflight();const prior=await api('/api/latest');if(prior.report)render(prior.report);}
  catch(err){message(err.message,true);}
  document.querySelectorAll('input[name="mode"]').forEach(input=>input.addEventListener('change',preflight));
  $('watchlist').addEventListener('input',()=>{clearTimeout(window.preflightTimer);window.preflightTimer=setTimeout(preflight,250)});
  $('save-settings').addEventListener('click',async()=>{try{const result=await api('/api/config',{method:'PUT',body:JSON.stringify(readSettings())});showSettings(result.config);message('Lens saved for the next scan.');await preflight();}catch(err){message(err.message,true);}});
  $('demo').addEventListener('click',()=>doRun('/api/demo',{}));
  $('run').addEventListener('click',()=>doRun('/api/scan',{mode:mode(),watchlist:$('watchlist').value}));
});
