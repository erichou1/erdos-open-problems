const state={data:null,sort:"solvability",query:""};
const $=selector=>document.querySelector(selector);
const esc=value=>String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const dt=value=>{const date=new Date(value);return Number.isNaN(date.valueOf())?String(value||""):date.toLocaleString([], {dateStyle:"medium",timeStyle:"short"})};
const DATA_URL=location.hostname.endsWith("vercel.app")
  ? "https://raw.githubusercontent.com/erichou1/erdos-open-problems/status-live/status_site/data.json"
  : "/data.json";
const AUTO_REFRESH_MS=60_000;
const typeset=root=>{if(root&&typeof window.renderMathInElement==="function")window.renderMathInElement(root,{delimiters:[{left:"\\[",right:"\\]",display:true},{left:"\\(",right:"\\)",display:false},{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],throwOnError:false,strict:"ignore",trust:false,ignoredTags:["script","noscript","style","textarea","pre","code"]})};
const bar=(value,label,kind="index")=>{const number=Math.max(0,Math.min(100,Number(value||0)));return `<div class="rank-bar ${kind}" title="${esc(label)}"><div><span>${esc(label)}</span><b>${number}${kind==="prior"?"%":""}</b></div><i><em style="width:${number}%"></em></i></div>`};

async function load(){
  $("#reloadButton").classList.add("loading");
  try{
    const response=await fetch(`${DATA_URL}?t=${Date.now()}`,{cache:"no-store"});
    if(!response.ok)throw new Error(`Ranking snapshot failed (${response.status})`);
    state.data=await response.json();render();
  }catch(error){$("#rankingRows").innerHTML=`<tr><td colspan="7"><div class="error-state">${esc(error.message)}</div></td></tr>`}
  finally{$("#reloadButton").classList.remove("loading")}
}
function ordered(){
  const q=state.query.trim().toLowerCase();
  const rows=(state.data?.ranking||[]).filter(row=>!q||[row.number,row.statement,row.progress?.stage].some(value=>String(value||"").toLowerCase().includes(q)));
  const score=row=>state.sort==="progress"?row.progress.percent:state.sort==="lean"?row.solvability.lean_route_estimate:state.sort==="compute"?row.solvability.finite_computation_estimate:row.solvability.score;
  return rows.sort((a,b)=>score(b)-score(a)||a.number-b.number);
}
function render(){
  const {campaign,generated_at,ranking_method}=state.data;
  $("#campaignName").textContent=campaign;$("#snapshotTime").textContent=`Auto-updates · snapshot ${dt(generated_at)}`;$("#healthDot").classList.add("ok");
  $("#methodNote").innerHTML=`<strong>${esc(ranking_method.name)}</strong><span>${esc(ranking_method.formula)}</span><b>${esc(ranking_method.warning)}</b>`;
  renderRows();
}
function renderRows(){
  const rows=ordered();
  const top=rows.slice(0,3);
  $("#topRanks").innerHTML=top.map((row,index)=>`<a href="/#problem=${row.number}" class="top-rank"><span>${index+1}</span><div><p class="eyebrow">ERDŐS #${row.number}</p><strong>${esc(row.statement)}</strong><small>Index ${row.solvability.index} · ${esc(row.progress.stage)}</small></div></a>`).join("");
  $("#rankingRows").innerHTML=rows.length?rows.map((row,index)=>`<tr class="ranking-row" tabindex="0" data-href="/#problem=${row.number}"><td><strong class="rank-number">${index+1}</strong><small>base #${row.solvability.rank}</small></td><td><a href="/#problem=${row.number}"><b>#${row.number}</b><span>${esc(row.statement)}</span></a></td><td>${bar(row.solvability.index,"pipeline fit")}</td><td>${bar(row.progress.percent,row.progress.stage,"progress")}</td><td>${bar(row.solvability.lean_route_estimate,"weak prior","prior")}</td><td>${bar(row.solvability.finite_computation_estimate,"weak prior","prior")}</td><td>${bar(row.solvability.verified_novel_resolution_prior,"weak prior","prior")}</td></tr>`).join(""):`<tr><td colspan="7" class="empty-row">No ranked problems match.</td></tr>`;
  $("#rankingCount").textContent=`Showing ${rows.length} campaign problems · ranking changes with the selected metric`;
  document.querySelectorAll(".ranking-row").forEach(row=>{row.onclick=event=>{if(!event.target.closest("a"))location.href=row.dataset.href};row.onkeydown=event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();location.href=row.dataset.href}}});
  typeset($("#rankingRows"));typeset($("#topRanks"));
}
$("#rankingSearch").addEventListener("input",event=>{state.query=event.target.value;renderRows()});
document.querySelectorAll("[data-sort]").forEach(button=>button.onclick=()=>{state.sort=button.dataset.sort;document.querySelectorAll("[data-sort]").forEach(item=>item.classList.toggle("active",item===button));renderRows()});
$("#reloadButton").onclick=load;document.addEventListener("keydown",event=>{if(event.key==="/"&&!event.metaKey&&!event.ctrlKey&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||"")){event.preventDefault();$("#rankingSearch").focus()}});
load();window.setInterval(()=>{if(!document.hidden)load()},AUTO_REFRESH_MS);
