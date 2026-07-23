const state = {data: null, query: "", loading: false, lastError: null};
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[ch]));
const dt = value => {
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? String(value || "")
    : date.toLocaleString([], {dateStyle: "medium", timeStyle: "short"});
};

// ── Live snapshot resolution (identical strategy to the status/ranking pages) ──
const LIVE_REPO = "erichou1/erdos-open-problems";
const DATA_URL = "/data.json";
const AUTO_REFRESH_MS = 60_000;
const REF_CACHE_MS = 75_000;
const SNAPSHOT_STALE_MS = 240_000;
const REF_CACHE_KEY = "egmra-status-live-ref-v1";
const immutableDataUrl = sha => `https://raw.githubusercontent.com/${LIVE_REPO}/${sha}/status_site/data.json`;
const cachedLiveRef = () => {
  try { const value = JSON.parse(localStorage.getItem(REF_CACHE_KEY) || "null"); return value?.sha ? value : null; }
  catch (_error) { return null; }
};
const rememberLiveRef = sha => {
  try { localStorage.setItem(REF_CACHE_KEY, JSON.stringify({sha, checkedAt: Date.now()})); } catch (_error) {}
};
async function dataUrl({force = false} = {}) {
  if (!location.hostname.endsWith("vercel.app")) return DATA_URL;
  const cached = cachedLiveRef();
  if (!force && cached && Date.now() - cached.checkedAt < REF_CACHE_MS) return immutableDataUrl(cached.sha);
  try {
    const ref = await fetch(`https://api.github.com/repos/${LIVE_REPO}/git/ref/heads/status-live?t=${Date.now()}`, {cache: "no-store"});
    if (ref.ok) {
      const body = await ref.json(), sha = body?.object?.sha;
      if (sha) { rememberLiveRef(sha); return immutableDataUrl(sha); }
    }
  } catch (_error) {}
  return `https://raw.githubusercontent.com/${LIVE_REPO}/status-live/status_site/data.json`;
}

const typeset = root => {
  if (root && typeof window.renderMathInElement === "function")
    window.renderMathInElement(root, {
      delimiters: [
        {left: "\\[", right: "\\]", display: true},
        {left: "\\(", right: "\\)", display: false},
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
      ],
      throwOnError: false, strict: "ignore", trust: false,
      ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
    });
};

const ageLabel = ms => ms < 60_000 ? "less than a minute ago"
  : ms < 3_600_000 ? `${Math.floor(ms / 60_000)}m ago`
  : `${Math.floor(ms / 3_600_000)}h ago`;

function updateSnapshotStatus(error = null) {
  if (!state.data) return;
  const generated = new Date(state.data.generated_at);
  const age = Math.max(0, Date.now() - generated.valueOf());
  const delayed = Number.isNaN(age) || age > SNAPSHOT_STALE_MS;
  const dot = $("#healthDot");
  dot.classList.toggle("ok", !error && !delayed);
  dot.classList.toggle("stale", Boolean(error) || delayed);
  const status = error ? "Update check failed" : delayed ? "Updates delayed" : "Live";
  $("#snapshotTime").textContent = `${status} · snapshot ${ageLabel(age)}`;
  $("#snapshotTime").title = `Generated ${dt(state.data.generated_at)}${error ? ` · ${error}` : ""}`;
}

async function load(options = {}) {
  if (state.loading) return;
  state.loading = true;
  $("#reloadButton").classList.add("loading");
  try {
    const url = await dataUrl(options);
    const response = await fetch(`${url}?t=${Date.now()}`, {cache: "no-store"});
    if (!response.ok) throw new Error(`Snapshot failed (${response.status})`);
    state.data = await response.json();
    state.lastError = null;
    render();
  } catch (error) {
    state.lastError = error.message;
    updateSnapshotStatus(error.message);
    if (!state.data) $("#spList").innerHTML = `<div class="error-state">${esc(error.message)}</div>`;
  } finally {
    state.loading = false;
    $("#reloadButton").classList.remove("loading");
  }
}

const badge = (value, kind) => `<span class="sp-badge ${esc(kind || value)}">${esc(value)}</span>`;

function chatLink(url, label) {
  if (!url) return "";
  return `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`;
}

function stageRow(stage) {
  const round = stage.round != null ? ` · round ${stage.round}` : "";
  const assess = stage.assessment ? badge(stage.assessment, stage.assessment) : "";
  const timedOut = stage.timed_out ? badge("timed out", "failed") : "";
  const chars = Number(stage.chars || 0).toLocaleString();
  const trunc = stage.text_truncated
    ? `<div class="sp-trunc">Truncated to ${Number(stage.text || "").length.toLocaleString()} of ${chars} chars — open the chat for the full text.</div>`
    : "";
  const openByDefault = stage.role === "response" ? "open" : "";
  return `<details class="sp-stage ${esc(stage.role)}" ${openByDefault}>
    <summary>
      <span class="k">${esc(stage.stage)} · ${esc(stage.role)}${esc(round)}</span>
      ${assess}${timedOut}
      <span class="meta">${chars} chars · ${esc(dt(stage.at))}</span>
    </summary>
    <pre class="sp-text">${esc(stage.text)}</pre>
    ${trunc}
  </details>`;
}

function problemCard(problem) {
  const stages = (problem.stages || []).map(stageRow).join("");
  const roundInfo = problem.max_rounds != null
    ? `round ${problem.round ?? 0}/${problem.max_rounds}` : `round ${problem.round ?? 0}`;
  const links = [
    chatLink(problem.research_conversation_url, "research chat"),
    chatLink(problem.adapt_conversation_url, "adapt chat"),
  ].filter(Boolean).join("");
  return `<details class="sp-card">
    <summary>
      <span class="sp-title">${esc(problem.title || problem.id)}<small>${esc(problem.id)}</small></span>
      ${badge(problem.status || "running", problem.status || "running")}
      <span class="sp-badge">${esc(problem.current_stage || "")}</span>
      <span class="sp-badge">${esc(roundInfo)}</span>
      <span class="sp-badge">updated ${esc(dt(problem.updated_at))}</span>
    </summary>
    <div class="sp-body">
      ${links ? `<div class="sp-links">${links}</div>` : ""}
      ${problem.problem_statement ? `<div class="sp-statement">${esc(problem.problem_statement)}</div>` : ""}
      ${stages || `<p class="sp-empty">No stages recorded yet.</p>`}
    </div>
  </details>`;
}

function render() {
  const pipeline = state.data.side_pipeline || {problems: [], summary: {}};
  $("#campaignName").textContent = "Side pipeline";
  updateSnapshotStatus(state.lastError);

  const summary = pipeline.summary || {};
  const metrics = [
    ["total", summary.total ?? 0],
    ["running", summary.running ?? 0],
    ["solved", summary.solved ?? 0],
    ["exhausted", summary.exhausted ?? 0],
    ["failed", summary.failed ?? 0],
  ];
  $("#spSummary").innerHTML = metrics
    .map(([label, value]) => `<div class="sp-metric"><b>${esc(value)}</b><span>${esc(label)}</span></div>`)
    .join("");

  renderList();
}

function renderList() {
  const pipeline = state.data.side_pipeline || {problems: []};
  const q = state.query.trim().toLowerCase();
  const problems = (pipeline.problems || []).filter(problem => !q ||
    [problem.id, problem.title, problem.problem_statement, problem.status, problem.current_stage]
      .some(value => String(value || "").toLowerCase().includes(q)));
  $("#spList").innerHTML = problems.length
    ? problems.map(problemCard).join("")
    : `<p class="sp-empty">No problems in the side pipeline yet. Start it with <code>side_pipeline.py</code>.</p>`;
  $("#spCount").textContent = `${problems.length} problem${problems.length === 1 ? "" : "s"} · each chat is named after its problem`;
  typeset($("#spList"));
}

$("#spSearch").addEventListener("input", event => { state.query = event.target.value; renderList(); });
$("#reloadButton").onclick = () => load({force: true});
window.addEventListener("online", () => load({force: true}));
document.addEventListener("visibilitychange", () => { if (!document.hidden) load(); });
document.addEventListener("keydown", event => {
  if (event.key === "/" && !event.metaKey && !event.ctrlKey &&
      !/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || "")) {
    event.preventDefault();
    $("#spSearch").focus();
  }
});
load();
window.setInterval(() => { if (!document.hidden) load(); }, AUTO_REFRESH_MS);
window.setInterval(() => updateSnapshotStatus(state.lastError), 30_000);
