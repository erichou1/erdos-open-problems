const state={data:null,filter:"all",query:"",ascending:true};
const $=s=>document.querySelector(s);
const esc=value=>String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const dt=value=>{if(!value)return "—";const date=new Date(value);return Number.isNaN(date.valueOf())?String(value):date.toLocaleString([], {dateStyle:"medium",timeStyle:"short"})};
const short=value=>{const text=String(value||"");return text.length>45?`${text.slice(0,20)}…${text.slice(-16)}`:text};
const statusClass=value=>String(value||"pending").toLowerCase().replace(/[^a-z]/g,"-");

const DATA_URL=location.hostname.endsWith("vercel.app")
  ? "https://raw.githubusercontent.com/erichou1/erdos-open-problems/audit/egmra-independent-remediation-20260713/status_site/data.json"
  : "/data.json";

async function load(){
  $("#reloadButton").classList.add("loading");
  try{
    const separator=DATA_URL.includes("?")?"&":"?";
    const response=await fetch(`${DATA_URL}${separator}t=${Date.now()}`,{cache:"no-store"});
    if(!response.ok)throw new Error(`Snapshot request failed (${response.status})`);
    state.data=await response.json();render();route();
  }catch(error){
    $("#problemRows").innerHTML=`<tr><td colspan="7"><div class="error-state">${esc(error.message)}</div></td></tr>`;
  }finally{$("#reloadButton").classList.remove("loading")}
}

function render(){
  const {campaign,generated_at,summary,workers,problems,aristotle_artifacts}=state.data;
  $("#campaignName").textContent=campaign;$("#snapshotTime").textContent=`Snapshot ${dt(generated_at)}`;$("#healthDot").classList.add("ok");
  const leased=summary.by_status.leased||0,pending=summary.by_status.pending||0,finished=(summary.by_status.done||0)+(summary.by_status.failed||0);
  const metrics=[[summary.total,"problems"],[leased,"actively leased"],[pending,"waiting"],[summary.total_runs,"run records"],[summary.aristotle_artifacts||aristotle_artifacts.length,"Aristotle artifacts"]];
  $("#metricStrip").innerHTML=metrics.map(([n,label])=>`<div class="metric"><strong>${esc(n)}</strong><span>${esc(label)}</span></div>`).join("");
  $("#workerCount").textContent=`${workers.length} active`;
  $("#workerBoard").innerHTML=workers.length?workers.map(w=>`<div class="worker-slot"><div><strong>${esc(w.worker)}</strong><a href="#problem=${w.number}">#${esc(w.number)}</a><small>${esc(w.status)}</small></div><i class="pulse"></i></div>`).join(""):`<div class="worker-slot"><small>No active leases in this snapshot.</small></div>`;
  renderBars(summary.by_status,summary.total);renderFilters(summary.by_status);renderRows();renderArtifacts(aristotle_artifacts);$("#artifactCount").textContent=aristotle_artifacts.length;
}

function renderBars(byStatus,total){
  const order=["leased","pending","retained","done","failed"];
  $("#statusBars").innerHTML=order.filter(k=>byStatus[k]).map(k=>`<div class="status-bar-line"><span>${esc(k)}</span><div class="bar-track"><div class="bar-fill ${statusClass(k)}" style="width:${Math.max(2,(byStatus[k]/total)*100)}%"></div></div><strong>${byStatus[k]}</strong></div>`).join("")||"<p>No status data.</p>";
}
function renderFilters(byStatus){
  const options=["all",...Object.keys(byStatus)];
  $("#statusFilters").innerHTML=options.map(k=>`<button class="segment ${state.filter===k?"active":""}" data-filter="${esc(k)}">${esc(k)}${k==="all"?"":` · ${byStatus[k]}`}</button>`).join("");
  document.querySelectorAll("[data-filter]").forEach(button=>button.onclick=()=>{state.filter=button.dataset.filter;renderFilters(byStatus);renderRows()});
}
function filteredProblems(){
  const q=state.query.trim().toLowerCase();
  return state.data.problems.filter(p=>(state.filter==="all"||p.status===state.filter)&&(!q||[p.number,p.statement,p.worker,p.latest_state,p.result_state].some(v=>String(v||"").toLowerCase().includes(q)))).sort((a,b)=>(a.number-b.number)*(state.ascending?1:-1));
}
function renderRows(){
  const rows=filteredProblems();
  $("#problemRows").innerHTML=rows.length?rows.map(p=>`<tr><td><div class="problem-name"><strong class="problem-number">#${esc(p.number)}</strong><span class="problem-statement" title="${esc(p.statement)}">${esc(p.statement)}</span></div></td><td><span class="status-chip ${statusClass(p.status)}">${esc(p.status)}</span></td><td><span class="worker-tag">${esc(p.worker||"—")}</span></td><td>${esc(p.attempts)}</td><td>${esc(p.latest_state||p.result_state||"—")}</td><td>${p.run_count} / ${p.chatgpt_run_count}</td><td><button class="open-row" data-open="${p.number}" aria-label="Open problem ${p.number}">→</button></td></tr>`).join(""):`<tr><td colspan="7" class="empty-row">No problems match this view.</td></tr>`;
  $("#resultCount").textContent=`Showing ${rows.length} of ${state.data.problems.length} problems · Runs / ChatGPT exchanges`;
  document.querySelectorAll("[data-open]").forEach(button=>button.onclick=()=>openProblem(Number(button.dataset.open)));
}
function renderArtifacts(artifacts){
  $("#artifactRail").innerHTML=artifacts.slice(0,12).map((a,index)=>`<article class="artifact-item"><strong>${esc(a.declarations?.[0]||a.artifact_id)}</strong><span>${esc(a.worker||"unassigned")} · ${a.bytes.toLocaleString()} B · ${esc(a.status)}</span><a href="#artifact=${encodeURIComponent(a.artifact_id)}" data-artifact="${index}">Inspect source preview →</a></article>`).join("");
  document.querySelectorAll("[data-artifact]").forEach(button=>button.onclick=()=>openArtifact(artifacts[Number(button.dataset.artifact)]));
}
function openProblem(number,runId=null){
  const p=state.data.problems.find(item=>item.number===number);if(!p)return;
  if(!runId)location.hash=`problem=${number}`;$("#detailTitle").textContent=`Erdős #${number}`;$("#erdosLink").href=p.erdos_page||"#";
  const meta=[[p.status,"status"],[p.worker||"—","worker"],[p.attempts,"attempts"],[p.latest_state||"—","latest outcome"]];
  const runs=p.runs.length?p.runs.map(run=>runHtml(run,p)).join(""):`<p class="missing-link">No completed run records yet.</p>`;
  const exchanges=p.exchanges?.length?`<table class="exchange-table">${p.exchanges.slice(0,40).map(x=>`<tr><td>${esc(x.stage)}</td><td>${esc(x.model)}</td><td>${x.conversation_url?`<a href="${esc(x.conversation_url)}" target="_blank" rel="noopener">Open ChatGPT ↗</a>`:`URL not recorded · ${esc(x.response_hash)}`}</td></tr>`).join("")}</table>`:`<p class="missing-link">No browser exchange records for this problem.</p>`;
  const aristotle=p.aristotle?.length?p.aristotle.map((a,i)=>`<details class="run-row"><summary><div><strong>${esc(a.declarations?.join(", ")||a.artifact_id)}</strong><span class="run-time">${esc(a.worker||"worker unknown")} · ${a.bytes.toLocaleString()} bytes</span></div><span class="run-state">quarantined</span></summary><div class="run-body"><pre class="source-preview">${esc(a.source_preview)}</pre></div></details>`).join(""):`<p class="missing-link">No Aristotle session can be reliably associated with this problem. Unlinked sessions remain in the global quarantine inventory.</p>`;
  $("#detailContent").innerHTML=`<p class="detail-statement">${esc(p.statement)}</p><div class="detail-meta">${meta.map(([v,k])=>`<div><small>${k}</small><strong>${esc(v)}</strong></div>`).join("")}</div>${p.result_state?`<p class="error-state">${esc(p.result_state)}</p>`:""}<section class="detail-section"><h3>Research runs · ${p.runs.length}</h3>${runs}</section><section class="detail-section"><h3>ChatGPT browser exchanges · ${p.exchanges?.length||0}</h3>${exchanges}</section><section class="detail-section"><h3>Associated Aristotle artifacts · ${p.aristotle?.length||0}</h3>${aristotle}</section>`;
  showPanel();
  if(runId){const row=[...document.querySelectorAll("[data-run-id]")].find(item=>item.dataset.runId===runId);if(row){row.open=true;requestAnimationFrame(()=>row.scrollIntoView({block:"start"}))}}
}
function runHtml(run,p){
  const links=run.chatgpt?.length?run.chatgpt.map(item=>`<a href="${esc(item.url)}" target="_blank" rel="noopener">ChatGPT · ${esc(item.stage)} ↗</a>`).join(""):`<span class="missing-link">ChatGPT URL not recorded</span>`;
  const permalink=`#problem=${p.number}&run=${encodeURIComponent(run.run_id)}`;
  return `<details class="run-row" data-run-id="${esc(run.run_id)}"><summary><div><strong class="run-id">${esc(short(run.run_id))}</strong><span class="run-time">${dt(run.started_at||run.recorded_at)} · ${esc(run.machine||"local")}</span></div><span class="run-state">${esc(run.state||"attempt log")}</span></summary><div class="run-body"><div class="run-grid"><div><strong>${run.event_count||0}</strong><small>events</small></div><div><strong>${run.claims_proposed||0}</strong><small>claims</small></div><div><strong>${run.evidence_attached||0}</strong><small>evidence</small></div><div><strong>${run.packet_reentries||0}</strong><small>reentries</small></div></div><div class="family-list">${(run.families||[]).map(f=>`<span>${esc(f)}</span>`).join("")||`<span>no branches recorded</span>`}</div><div class="link-list" style="margin-top:12px"><a href="${permalink}">Permanent run link</a>${links}</div></div></details>`;
}
function openArtifact(a){
  if(!location.hash.startsWith("#artifact="))location.hash=`artifact=${encodeURIComponent(a.artifact_id)}`;
  $("#detailTitle").textContent="Aristotle artifact";$("#erdosLink").href="#";
  $("#detailContent").innerHTML=`<p class="detail-statement">${esc(a.declarations?.join(", ")||"Unnamed Lean candidate")}</p><div class="detail-meta"><div><small>worker</small><strong>${esc(a.worker||"—")}</strong></div><div><small>session</small><strong>${esc(short(a.session||"—"))}</strong></div><div><small>bytes</small><strong>${a.bytes.toLocaleString()}</strong></div><div><small>authority</small><strong>quarantined</strong></div></div><p class="missing-link">No public Aristotle vendor URL is stored. This is the local quarantined source preview; it is not proof evidence until kernel replay and correspondence review pass.</p><pre class="source-preview">${esc(a.source_preview)}</pre>`;showPanel();
}
function showPanel(){$("#detailPanel").classList.add("open");$("#detailPanel").setAttribute("aria-hidden","false");$("#scrim").hidden=false}
function closePanel(){$("#detailPanel").classList.remove("open");$("#detailPanel").setAttribute("aria-hidden","true");$("#scrim").hidden=true;if(location.hash.startsWith("#problem="))history.replaceState(null,"",location.pathname)}
function route(){
  if(!state.data)return;
  const problem=location.hash.match(/^#problem=(\d+)(?:&run=(.+))?$/);
  if(problem){openProblem(Number(problem[1]),problem[2]?decodeURIComponent(problem[2]):null);return}
  const artifact=location.hash.match(/^#artifact=(.+)$/);
  if(artifact){const id=decodeURIComponent(artifact[1]);const row=state.data.aristotle_artifacts.find(item=>item.artifact_id===id);if(row)openArtifact(row)}
}
$("#searchInput").addEventListener("input",event=>{state.query=event.target.value;renderRows()});
$("#sortButton").onclick=event=>{state.ascending=!state.ascending;event.target.textContent=`Sort: number ${state.ascending?"↑":"↓"}`;renderRows()};
$("#reloadButton").onclick=load;$("#closeDetail").onclick=closePanel;$("#scrim").onclick=closePanel;window.addEventListener("hashchange",route);document.addEventListener("keydown",event=>{if(event.key==="Escape")closePanel()});
load();