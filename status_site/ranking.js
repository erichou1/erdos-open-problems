const state={data:null,sort:"allocation",query:"",loading:false,lastLoadError:null};
const $=selector=>document.querySelector(selector);
const esc=value=>String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const dt=value=>{const date=new Date(value);return Number.isNaN(date.valueOf())?String(value||""):date.toLocaleString([], {dateStyle:"medium",timeStyle:"short"})};
const LIVE_REPO="erichou1/erdos-open-problems";
const DATA_URL="/data.json";
const AUTO_REFRESH_MS=60_000;
const REF_CACHE_MS=75_000;
const SNAPSHOT_STALE_MS=240_000;
const REF_CACHE_KEY="egmra-status-live-ref-v1";
const immutableDataUrl=sha=>`https://raw.githubusercontent.com/${LIVE_REPO}/${sha}/status_site/data.json`;
const cachedLiveRef=()=>{try{const value=JSON.parse(localStorage.getItem(REF_CACHE_KEY)||"null");return value?.sha?value:null}catch(_error){return null}};
const rememberLiveRef=sha=>{try{localStorage.setItem(REF_CACHE_KEY,JSON.stringify({sha,checkedAt:Date.now()}))}catch(_error){}};
async function dataUrl({force=false}={}){if(!location.hostname.endsWith("vercel.app"))return DATA_URL;const cached=cachedLiveRef();if(!force&&cached&&Date.now()-cached.checkedAt<REF_CACHE_MS)return immutableDataUrl(cached.sha);try{const ref=await fetch(`https://api.github.com/repos/${LIVE_REPO}/git/ref/heads/status-live?t=${Date.now()}`,{cache:"no-store"});if(ref.ok){const body=await ref.json(),sha=body?.object?.sha;if(sha){rememberLiveRef(sha);return immutableDataUrl(sha)}}}catch(_error){}return `https://raw.githubusercontent.com/${LIVE_REPO}/status-live/status_site/data.json`}
const typeset=root=>{if(root&&typeof window.renderMathInElement==="function")window.renderMathInElement(root,{delimiters:[{left:"\\[",right:"\\]",display:true},{left:"\\(",right:"\\)",display:false},{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],throwOnError:false,strict:"ignore",trust:false,ignoredTags:["script","noscript","style","textarea","pre","code"]})};
const bar=(value,label,kind="index")=>{const number=Math.max(0,Math.min(100,Number(value||0)));return `<div class="rank-bar ${kind}" title="${esc(label)}"><div><span>${esc(label)}</span><b>${number}${kind==="prior"?"%":""}</b></div><i><em style="width:${number}%"></em></i></div>`};
const fixed=value=>Number(value||0).toFixed(4);
const signed=value=>{const number=Number(value||0);return `${number>0?"+":""}${number.toFixed(4)}`};
const scoreCell=(value,label,kind="")=>`<div class="score-cell ${kind}"><span>${esc(label)}</span><strong>${kind==="adjustment"?signed(value):fixed(value)}</strong></div>`;
const badge=(value,kind)=>`<span class="ranking-badge ${esc(kind)}">${esc(value)}</span>`;

const ageLabel=milliseconds=>milliseconds<60_000?"less than a minute ago":milliseconds<3_600_000?`${Math.floor(milliseconds/60_000)}m ago`:`${Math.floor(milliseconds/3_600_000)}h ago`;
function updateSnapshotStatus(error=null){if(!state.data)return;const generated=new Date(state.data.generated_at),age=Math.max(0,Date.now()-generated.valueOf()),delayed=Number.isNaN(age)||age>SNAPSHOT_STALE_MS,dot=$("#healthDot");dot.classList.toggle("ok",!error&&!delayed);dot.classList.toggle("stale",Boolean(error)||delayed);const status=error?"Update check failed":delayed?"Updates delayed":"Live";$("#snapshotTime").textContent=`${status} · snapshot ${ageLabel(age)}`;$("#snapshotTime").title=`Generated ${dt(state.data.generated_at)}${error?` · ${error}`:""}`}
async function load(options={}){
  if(state.loading)return;
  state.loading=true;
  $("#reloadButton").classList.add("loading");
  try{
    const url=await dataUrl(options);
    const response=await fetch(`${url}?t=${Date.now()}`,{cache:"no-store"});
    if(!response.ok)throw new Error(`Ranking snapshot failed (${response.status})`);
    state.data=await response.json();state.lastLoadError=null;render();
  }catch(error){state.lastLoadError=error.message;updateSnapshotStatus(error.message);if(!state.data)$("#rankingRows").innerHTML=`<tr><td colspan="8"><div class="error-state">${esc(error.message)}</div></td></tr>`}
  finally{state.loading=false;$("#reloadButton").classList.remove("loading")}
}
function ordered(){
  const q=state.query.trim().toLowerCase();
  const rows=(state.data?.ranking||[]).filter(row=>!q||[row.number,row.statement,row.progress?.stage,row.prize_status,row.literature_coverage_status,row.reason_selected].some(value=>String(value||"").toLowerCase().includes(q)));
  if(state.sort==="allocation")return rows.sort((a,b)=>a.allocation_rank-b.allocation_rank);
  const score=row=>state.sort==="progress"?row.progress.percent:state.sort==="literature"?row.literature_adjustment:row.selection_score;
  return rows.sort((a,b)=>score(b)-score(a)||a.allocation_rank-b.allocation_rank);
}
function render(){
  const {campaign,generated_at,ranking_method}=state.data;
  $("#campaignName").textContent=campaign;updateSnapshotStatus();
  $("#methodNote").innerHTML=`<strong>${esc(ranking_method.name)}</strong><span>${esc(ranking_method.formula)}</span><b>${esc(ranking_method.warning)}</b>`;
  renderRows();
}
function renderRows(){
  const rows=ordered();
  const top=rows.slice(0,3);
  $("#topRanks").innerHTML=top.map(row=>`<a href="/#problem=${row.number}" class="top-rank"><span>${row.allocation_rank}</span><div><p class="eyebrow">ERDŐS #${row.number} · ${esc(row.prize_status)}</p><strong>${esc(row.statement)}</strong><small>Final ${fixed(row.selection_score)} · ${esc(row.progress.stage)}</small></div></a>`).join("");
  $("#rankingRows").innerHTML=rows.length?rows.map(row=>`<tr class="ranking-row" tabindex="0" data-href="/#problem=${row.number}"><td><strong class="rank-number">${row.allocation_rank}</strong><small>shared allocation</small></td><td><a href="/#problem=${row.number}"><b>#${row.number}</b><span>${esc(row.statement)}</span></a></td><td>${bar(row.progress.percent,row.progress.stage,"progress")}</td><td>${badge(row.prize_status,row.prize_status)}</td><td>${badge(row.literature_coverage_status,"literature")}</td><td>${scoreCell(row.base_acquisition_score,"base")}</td><td>${scoreCell(row.literature_adjustment,"literature","adjustment")}</td><td>${scoreCell(row.selection_score,"final","final")}</td></tr>`).join(""):`<tr><td colspan="8" class="empty-row">No ranked problems match.</td></tr>`;
  $("#rankingCount").textContent=`Showing ${rows.length} current allocation problems · default order is shared by every worker`;
  document.querySelectorAll(".ranking-row").forEach(row=>{row.onclick=event=>{if(!event.target.closest("a"))location.href=row.dataset.href};row.onkeydown=event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();location.href=row.dataset.href}}});
  typeset($("#rankingRows"));typeset($("#topRanks"));
}
$("#rankingSearch").addEventListener("input",event=>{state.query=event.target.value;renderRows()});
document.querySelectorAll("[data-sort]").forEach(button=>button.onclick=()=>{state.sort=button.dataset.sort;document.querySelectorAll("[data-sort]").forEach(item=>item.classList.toggle("active",item===button));renderRows()});
$("#reloadButton").onclick=()=>load({force:true});window.addEventListener("online",()=>load({force:true}));document.addEventListener("visibilitychange",()=>{if(!document.hidden)load()});document.addEventListener("keydown",event=>{if(event.key==="/"&&!event.metaKey&&!event.ctrlKey&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||"")){event.preventDefault();$("#rankingSearch").focus()}});
load();window.setInterval(()=>{if(!document.hidden)load()},AUTO_REFRESH_MS);window.setInterval(()=>updateSnapshotStatus(state.lastLoadError),30_000);
