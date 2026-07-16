const state={data:null,filter:"all",query:"",ascending:true};
const $=s=>document.querySelector(s);
const esc=value=>String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const dt=value=>{if(!value)return "—";const date=new Date(value);return Number.isNaN(date.valueOf())?String(value):date.toLocaleString([], {dateStyle:"medium",timeStyle:"short"})};
const short=value=>{const text=String(value||"");return text.length>45?`${text.slice(0,20)}…${text.slice(-16)}`:text};
const statusClass=value=>String(value||"pending").toLowerCase().replace(/[^a-z]/g,"-");
const STATUS_LABELS={leased:"Working now",pending:"Waiting",retained:"Paused for retry",done:"Finished",failed:"Stopped with error"};
const RESULT_LABELS={BLOCKED_BY_INTERPRETATION:"Needs clarification",OPEN_NO_PROGRESS:"No verified progress yet",COMPUTATIONAL_EVIDENCE:"Computer-checked partial result",CANDIDATE_SOLUTION:"Possible solution found",CANDIDATE_DISPROOF:"Possible counterexample found",VERIFIED_CANDIDATE:"Candidate independently checked",FORMALLY_VERIFIED_CANDIDATE:"Lean proof independently checked"};
const ACTION_LABELS={PROBLEM_FROZEN:"Saved the exact problem statement",INTERPRETATION_ADDED:"Recorded the intended meaning",INTENT_CERTIFICATE_ISSUED:"Approved the problem interpretation",BRANCH_OPENED:"Started a research approach",CLAIM_PROPOSED:"Proposed a mathematical statement",CLAIM_PROMOTED:"Accepted a supported statement",EVIDENCE_ATTACHED:"Attached independently checked evidence",PACKET_REENTRY:"Searched sources for a new subproblem",FORMAL_CORRESPONDENCE_ISSUED:"Matched the informal claim to Lean",MODEL_EXCHANGE_RECORDED:"Recorded a ChatGPT exchange",BRANCH_CLOSED:"Finished a research approach",GATE_DECIDED:"Checked whether the result can advance"};
const statusLabel=value=>STATUS_LABELS[value]||String(value||"Unknown").replaceAll("_"," ").toLowerCase();
const resultLabel=value=>RESULT_LABELS[value]||String(value||"Not finished").replaceAll("_"," ").toLowerCase();
const actionLabel=value=>ACTION_LABELS[value]||String(value||"Recorded a step").replaceAll("_"," ").toLowerCase();
const workerLabel=value=>{
  if(!value)return "Not assigned";
  const machine=(state.data?.machines||[]).find(item=>(item.worker_ids||[]).includes(value));
  const slot=String(value).split(":").pop();
  return machine?`${machine.hostname} · ${slot}`:String(value);
};
const problemStatusLabel=problem=>problem.status==="leased"
  && problem.worker_liveness==="stale"
  ? "Lease stale — waiting to reassign"
  : statusLabel(problem.status);
const progressHtml=progress=>{
  const value=Math.max(0,Math.min(100,Number(progress?.percent||0)));
  return `<div class="progress-block" title="${esc(progress?.disclaimer||"")}"><div class="progress-heading"><span>${esc(progress?.stage||"Queued")}</span><b>${value}</b></div><div class="progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${value}" aria-label="Research milestone ${value} of 100"><i style="width:${value}%"></i></div></div>`;
};
const typeset=root=>{
  if(!root||typeof window.renderMathInElement!=="function")return;
  window.renderMathInElement(root,{
    delimiters:[
      {left:"\\[",right:"\\]",display:true},
      {left:"\\(",right:"\\)",display:false},
      {left:"$$",right:"$$",display:true},
      {left:"$",right:"$",display:false}
    ],
    throwOnError:false,
    strict:"ignore",
    trust:false,
    ignoredTags:["script","noscript","style","textarea","pre","code"]
  });
};

const LIVE_REPO="erichou1/erdos-open-problems";
const DATA_URL="/data.json";
// GitHub's raw branch URL can lag the actual force-updated ref by minutes.
// Resolve the ref first, then fetch the immutable SHA URL. Two-minute polling
// stays within GitHub's unauthenticated 60 requests/hour limit per viewer.
const AUTO_REFRESH_MS=120_000;
async function dataUrl(){
  if(!location.hostname.endsWith("vercel.app"))return DATA_URL;
  try{
    const ref=await fetch(`https://api.github.com/repos/${LIVE_REPO}/git/ref/heads/status-live?t=${Date.now()}`,{cache:"no-store"});
    if(ref.ok){const body=await ref.json();const sha=body?.object?.sha;if(sha)return `https://raw.githubusercontent.com/${LIVE_REPO}/${sha}/status_site/data.json`}
  }catch(_error){}
  return `https://raw.githubusercontent.com/${LIVE_REPO}/status-live/status_site/data.json`;
}

async function load(){
  $("#reloadButton").classList.add("loading");
  try{
    const url=await dataUrl();
    const separator=url.includes("?")?"&":"?";
    const response=await fetch(`${url}${separator}t=${Date.now()}`,{cache:"no-store"});
    if(!response.ok)throw new Error(`Snapshot request failed (${response.status})`);
    state.data=await response.json();render();route();
  }catch(error){
    $("#problemRows").innerHTML=`<tr><td colspan="7"><div class="error-state">${esc(error.message)}</div></td></tr>`;
  }finally{$("#reloadButton").classList.remove("loading")}
}

function render(){
  const {campaign,generated_at,summary,workers,problems,aristotle_artifacts,machines=[]}=state.data;
  $("#campaignName").textContent=campaign;$("#snapshotTime").textContent=`Auto-updates · snapshot ${dt(generated_at)}`;$("#healthDot").classList.add("ok");
  const leased=summary.by_status.leased||0,pending=summary.by_status.pending||0;
  const metrics=[[summary.total,"problems being tracked"],[leased,"being worked on now"],[summary.computers_active||0,"computers active"],[summary.total_runs,"research attempts logged"],[summary.aristotle_artifacts||aristotle_artifacts.length,"formal proof drafts"]];
  $("#metricStrip").innerHTML=metrics.map(([n,label])=>`<div class="metric"><strong>${esc(n)}</strong><span>${esc(label)}</span></div>`).join("");
  const activeWorkers=workers.filter(worker=>worker.active).length;
  const liveWorkers=workers.filter(worker=>worker.active);
  const staleWorkers=workers.filter(worker=>!worker.active);
  document.querySelector(".stale-leases")?.remove();
  $("#workerCount").textContent=`${activeWorkers} active`;
  const liveCards=liveWorkers.map(w=>`<div class="worker-slot"><div><strong>${esc(workerLabel(w.worker))}</strong><a href="#problem=${w.number}">#${esc(w.number)}</a><small>Working now</small></div><i class="pulse"></i></div>`).join("");
  const staleDetails=staleWorkers.length?`<details class="stale-leases"><summary>${staleWorkers.length} old leases waiting to expire — not active work</summary><div>${staleWorkers.map(w=>`<a href="#problem=${w.number}">#${esc(w.number)}</a>`).join("")}</div></details>`:"";
  $("#workerBoard").innerHTML=liveCards||`<div class="worker-slot"><small>No computer is actively working in this snapshot.</small></div>`;
  $("#workerBoard").insertAdjacentHTML("afterend",staleDetails);
  renderMachines(machines);renderBars(summary.by_status,summary.total);renderFilters(summary.by_status);renderRows();renderArtifacts(aristotle_artifacts);$("#artifactCount").textContent=aristotle_artifacts.length;$("#artifactLinkNote").textContent=`${summary.aristotle_linked||0} safely linked to a specific problem · ${summary.aristotle_unlinked||0} older drafts cannot be linked reliably`;
}

function renderMachines(machines){
  const active=machines.filter(machine=>machine.activity==="active").length;
  $("#computerSummary").textContent=`${active} active · ${machines.length} known`;
  $("#computerBoard").innerHTML=machines.length?machines.map(machine=>{
    const versionLabel={current:"Current",outdated:"Update needed",ahead:"Ahead of remote",diverged:"Different branch history",unknown:"Version unknown"}[machine.version_status]||machine.version_status;
    const problems=(machine.current_problems||[]).map(pid=>{const number=String(pid).split("-").pop();return `<a href="#problem=${number}">#${esc(number)}</a>`}).join("")||`<span>no problem leased</span>`;
    const age=machine.heartbeat_age_seconds==null?"no heartbeat":machine.heartbeat_age_seconds<60?`${machine.heartbeat_age_seconds}s ago`:`${Math.floor(machine.heartbeat_age_seconds/60)}m ago`;
    return `<article class="computer-card ${esc(machine.activity)}"><div class="computer-title"><span class="machine-dot"></span><div><strong>${esc(machine.hostname)}</strong><small>${esc(machine.machine_id)}</small></div><b>${esc(machine.activity)}</b></div><dl><div><dt>Version</dt><dd class="version-${esc(machine.version_status)}">${esc(versionLabel)}</dd></div><div><dt>Commit</dt><dd>${esc(String(machine.code_commit||"unknown").slice(0,8))}</dd></div><div><dt>Worker slots</dt><dd>${esc(machine.worker_slots)}</dd></div><div><dt>Heartbeat</dt><dd>${esc(age)}</dd></div></dl><div class="computer-problems"><span>Working on</span>${problems}</div></article>`;
  }).join(""):`<div class="empty-machine"><strong>No computer heartbeat has been recorded yet.</strong><p>Restart a campaign process on the machine-registry build to register it here.</p></div>`;
}

function renderBars(byStatus,total){
  const order=["leased","pending","retained","done","failed"];
  $("#statusBars").innerHTML=order.filter(k=>byStatus[k]).map(k=>`<div class="status-bar-line"><span>${esc(statusLabel(k))}</span><div class="bar-track"><div class="bar-fill ${statusClass(k)}" style="width:${Math.max(2,(byStatus[k]/total)*100)}%"></div></div><strong>${byStatus[k]}</strong></div>`).join("")||"<p>No status data.</p>";
}
function renderFilters(byStatus){
  const options=["all",...Object.keys(byStatus)];
  $("#statusFilters").innerHTML=options.map(k=>`<button class="segment ${state.filter===k?"active":""}" data-filter="${esc(k)}">${k==="all"?"All problems":esc(statusLabel(k))}${k==="all"?"":` · ${byStatus[k]}`}</button>`).join("");
  document.querySelectorAll("[data-filter]").forEach(button=>button.onclick=()=>{state.filter=button.dataset.filter;renderFilters(byStatus);renderRows()});
}
function filteredProblems(){
  const q=state.query.trim().toLowerCase();
  return state.data.problems.filter(p=>(state.filter==="all"||p.status===state.filter)&&(!q||[p.number,p.statement,p.worker,p.latest_state,p.result_state].some(v=>String(v||"").toLowerCase().includes(q)))).sort((a,b)=>(a.number-b.number)*(state.ascending?1:-1));
}
function renderRows(){
  const rows=filteredProblems();
  $("#problemRows").innerHTML=rows.length?rows.map(p=>`<tr class="problem-row" data-row="${p.number}" tabindex="0" aria-label="Open Erdős problem ${p.number}"><td><div class="problem-name"><strong class="problem-number">#${esc(p.number)}</strong><span class="problem-statement" title="${esc(p.statement)}">${esc(p.statement)}</span></div></td><td><span class="status-chip ${p.worker_liveness==="stale"?"retained":statusClass(p.status)}">${esc(problemStatusLabel(p))}</span></td><td><span class="worker-tag">${esc(p.worker_liveness==="stale"?"No active computer":workerLabel(p.worker))}</span></td><td>${esc(p.attempts)}</td><td>${progressHtml(p.progress)}</td><td>${esc(resultLabel(p.latest_state||p.result_state))}</td><td>${p.run_count} / ${p.chatgpt_run_count}</td><td><button class="open-row" data-open="${p.number}" aria-label="Open problem ${p.number}">→</button></td></tr>`).join(""):`<tr><td colspan="8" class="empty-row">No problems match this view.</td></tr>`;
  $("#resultCount").textContent=`Showing ${rows.length} of ${state.data.problems.length} problems · research attempts / saved ChatGPT exchanges`;
  document.querySelectorAll("[data-open]").forEach(button=>button.onclick=()=>openProblem(Number(button.dataset.open)));
  document.querySelectorAll("[data-row]").forEach(row=>{
    row.onclick=event=>{if(!event.target.closest("button,a"))openProblem(Number(row.dataset.row))};
    row.onkeydown=event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();openProblem(Number(row.dataset.row))}};
  });
  typeset($("#problemRows"));
}
function renderArtifacts(artifacts){
  $("#artifactRail").innerHTML=artifacts.slice(0,12).map((a,index)=>`<article class="artifact-item"><strong>${esc(a.declarations?.[0]||a.artifact_id)}</strong><span>${esc(a.worker||"worker unknown")} · ${a.bytes.toLocaleString()} B · ${esc(a.status)}</span><a href="#artifact=${encodeURIComponent(a.artifact_id)}" data-artifact="${index}">See proof draft →</a></article>`).join("");
  document.querySelectorAll("[data-artifact]").forEach(button=>button.onclick=()=>openArtifact(artifacts[Number(button.dataset.artifact)]));
}
function openProblem(number,runId=null){
  const p=state.data.problems.find(item=>item.number===number);if(!p)return;
  if(!runId)location.hash=`problem=${number}`;$("#detailTitle").textContent=`Erdős #${number}`;$("#erdosLink").href=p.erdos_page||"#";
  const meta=[[problemStatusLabel(p),"work status"],[p.worker_liveness==="stale"?"No active computer":workerLabel(p.worker),"worker"],[p.attempts,"times tried"],[resultLabel(p.latest_state||p.result_state),"latest result"]];
  const runs=p.runs.length?p.runs.map(run=>runHtml(run,p)).join(""):`<p class="missing-link">No completed run records yet.</p>`;
  const exchanges=p.exchanges?.length?`<table class="exchange-table"><thead><tr><th>Step</th><th>Model</th><th>Chat</th></tr></thead><tbody>${p.exchanges.slice(0,40).map(x=>`<tr><td>${esc(x.stage)}</td><td>${esc(x.model)}</td><td>${x.conversation_url?`<a href="${esc(x.conversation_url)}" target="_blank" rel="noopener">Open exact ChatGPT chat ↗</a>`:`Older exchange: chat link was not saved · ${esc(x.response_hash)}`}</td></tr>`).join("")}</tbody></table>`:`<p class="missing-link">No saved ChatGPT exchanges for this problem yet.</p>`;
  const aristotle=p.aristotle?.length?p.aristotle.map((a,i)=>`<details class="run-row"><summary><div><strong>${esc(a.declarations?.join(", ")||a.artifact_id)}</strong><span class="run-time">${esc(a.worker||"worker unknown")} · ${a.bytes.toLocaleString()} bytes</span></div><span class="run-state">not yet verified</span></summary><div class="run-body"><pre class="source-preview">${esc(a.source_preview)}</pre></div></details>`).join(""):`<p class="explanation-note"><strong>0 linked drafts does not mean Aristotle was not used.</strong> It means no saved Aristotle file safely names this problem. Most older drafts lack a problem number, so the dashboard keeps them in the global list instead of guessing.</p>`;
  const progress=p.progress||{percent:5,stage:"Queued",explanation:"The problem is in the campaign.",milestones:[]};
  const milestoneList=(progress.milestones||[]).map(item=>`<li class="${item.achieved?"achieved":""}"><i>${item.achieved?"✓":""}</i><span>${esc(item.label)}</span></li>`).join("");
  $("#detailContent").innerHTML=`<p class="detail-statement">${esc(p.statement)}</p><div class="detail-meta">${meta.map(([v,k])=>`<div><small>${k}</small><strong>${esc(v)}</strong></div>`).join("")}</div><section class="progress-detail"><div><p class="eyebrow">RESEARCH MILESTONE — NOT SOLUTION PROBABILITY</p><h3>${esc(progress.stage)} · ${progress.percent}/100</h3><p>${esc(progress.explanation)}</p>${progressHtml(progress)}</div><ol>${milestoneList}</ol></section><nav class="detail-jumps" aria-label="Problem detail sections"><button data-jump="detail-runs">Attempts <b>${p.runs.length}</b></button><button data-jump="detail-exchanges">ChatGPT <b>${p.exchanges?.length||0}</b></button><button data-jump="detail-aristotle">Proof drafts <b>${p.aristotle?.length||0}</b></button></nav>${p.result_state?`<p class="error-state"><strong>Technical note:</strong> ${esc(p.result_state)}</p>`:""}<section id="detail-runs" class="detail-section"><h3>Research attempts · ${p.runs.length}</h3>${runs}</section><section id="detail-exchanges" class="detail-section"><h3>Saved ChatGPT exchanges · ${p.exchanges?.length||0}</h3>${exchanges}</section><section id="detail-aristotle" class="detail-section"><h3>Safely linked Aristotle proof drafts · ${p.aristotle?.length||0}</h3>${aristotle}</section>`;
  document.querySelectorAll("[data-jump]").forEach(button=>button.onclick=()=>document.getElementById(button.dataset.jump)?.scrollIntoView({block:"start"}));
  typeset($("#detailContent"));
  showPanel();
  if(runId){const row=[...document.querySelectorAll("[data-run-id]")].find(item=>item.dataset.runId===runId);if(row){row.open=true;requestAnimationFrame(()=>row.scrollIntoView({block:"start"}))}}
}
function runHtml(run,p){
  const links=run.chatgpt?.length?run.chatgpt.map(item=>`<a href="${esc(item.url)}" target="_blank" rel="noopener">Open ChatGPT chat for ${esc(item.stage)} ↗</a>`).join(""):`<span class="missing-link">This older attempt did not save its ChatGPT URL</span>`;
  const eventTimeline=(run.events||[]).length?`<div class="event-list"><h4>What happened in this attempt</h4><ol>${run.events.map(event=>`<li><span class="event-number">${esc(event.sequence)}</span><div><strong>${esc(actionLabel(event.action))}</strong><small>${esc(event.description||event.stage||dt(event.timestamp))}</small></div>${event.conversation_url?`<a href="${esc(event.conversation_url)}" target="_blank" rel="noopener">Open ChatGPT ↗</a>`:""}</li>`).join("")}</ol></div>`:"";
  const permalink=`#problem=${p.number}&run=${encodeURIComponent(run.run_id)}`;
  return `<details class="run-row" data-run-id="${esc(run.run_id)}"><summary><div><strong class="run-id">${esc(short(run.run_id))}</strong><span class="run-time">${dt(run.started_at||run.recorded_at)} · ${esc(run.machine||"local")}</span></div><span class="run-state">${esc(run.state?resultLabel(run.state):"Attempt log")}</span></summary><div class="run-body"><div class="run-grid"><div><strong>${run.event_count||0}</strong><small>steps logged</small></div><div><strong>${run.claims_proposed||0}</strong><small>math statements proposed</small></div><div><strong>${run.evidence_attached||0}</strong><small>checked evidence items</small></div><div><strong>${run.packet_reentries||0}</strong><small>new source searches</small></div></div><div class="family-list">${(run.families||[]).map(f=>`<span>${esc(f.replaceAll("_"," "))}</span>`).join("")||`<span>No research approach recorded</span>`}</div><div class="link-list" style="margin-top:12px"><a href="${permalink}">Copyable attempt link</a>${links}</div>${eventTimeline}</div></details>`;
}
function openArtifact(a){
  if(!location.hash.startsWith("#artifact="))location.hash=`artifact=${encodeURIComponent(a.artifact_id)}`;
  $("#detailTitle").textContent="Aristotle proof draft";$("#erdosLink").href="#";
  $("#detailContent").innerHTML=`<p class="detail-statement">${esc(a.declarations?.join(", ")||"Unnamed Lean proof draft")}</p><div class="detail-meta"><div><small>worker</small><strong>${esc(a.worker||"Unknown")}</strong></div><div><small>session</small><strong>${esc(short(a.session||"—"))}</strong></div><div><small>file size</small><strong>${a.bytes.toLocaleString()} bytes</strong></div><div><small>verification</small><strong>Not yet verified</strong></div></div><p class="explanation-note"><strong>What this means:</strong> Aristotle generated this Lean code, but the pipeline does not treat it as a proof until an independent Lean kernel checks it and the formal statement is confirmed to match the original problem.</p><pre class="source-preview">${esc(a.source_preview)}</pre>`;showPanel();
}
function showPanel(){$("#detailPanel").classList.add("open");$("#detailPanel").setAttribute("aria-hidden","false");$("#scrim").hidden=false;document.body.classList.add("panel-open")}
function closePanel(){$("#detailPanel").classList.remove("open");$("#detailPanel").setAttribute("aria-hidden","true");$("#scrim").hidden=true;document.body.classList.remove("panel-open");if(location.hash.startsWith("#problem=")||location.hash.startsWith("#artifact="))history.replaceState(null,"",location.pathname)}
function route(){
  if(!state.data)return;
  const problem=location.hash.match(/^#problem=(\d+)(?:&run=(.+))?$/);
  if(problem){openProblem(Number(problem[1]),problem[2]?decodeURIComponent(problem[2]):null);return}
  const artifact=location.hash.match(/^#artifact=(.+)$/);
  if(artifact){const id=decodeURIComponent(artifact[1]);const row=state.data.aristotle_artifacts.find(item=>item.artifact_id===id);if(row)openArtifact(row)}
}
$("#searchInput").addEventListener("input",event=>{state.query=event.target.value;renderRows()});
$("#sortButton").onclick=event=>{state.ascending=!state.ascending;event.target.textContent=`Sort: number ${state.ascending?"↑":"↓"}`;renderRows()};
$("#reloadButton").onclick=load;$("#closeDetail").onclick=closePanel;$("#scrim").onclick=closePanel;window.addEventListener("hashchange",route);document.addEventListener("keydown",event=>{if(event.key==="Escape")closePanel();if(event.key==="/"&&!event.metaKey&&!event.ctrlKey&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||"")){event.preventDefault();$("#searchInput").focus()}});
load();
window.setInterval(()=>{if(!document.hidden)load()},AUTO_REFRESH_MS);