/* CCNA 200-301 v1.1 practice runner.
 *
 * Deliberate constraints, mirroring the real delivery:
 *   - a confirmed answer is final; there is no back, skip, or flag
 *   - the clock never pauses and submits the attempt when it hits zero
 *   - no score, no correctness feedback, nothing but a counter during the run
 *   - no localStorage anywhere, so the core flow works with storage disabled
 */
'use strict';

const MIN_PER_Q = 1.2;          // 100 questions / 120 minutes
const LOW_AT = 10 * 60;         // amber
const CRIT_AT = 2 * 60;         // red, and the only point anything moves

const $ = (id) => document.getElementById(id);

let bank = null;
let run = null;                 // active attempt, null when not running
let tick = null;

/* ── helpers ──────────────────────────────────────────────────────────── */

function shuffle(a) {
  const out = a.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function clock(sec) {
  sec = Math.max(0, Math.round(sec));
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const mm = String(m).padStart(2, '0');
  const ss = String(s).padStart(2, '0');
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

function pct(n, d) { return d === 0 ? 0 : Math.round((n / d) * 1000) / 10; }

const looksLikeCommand = (t) =>
  /^(ip |ipv6 |no |show |network |standby |router |interface |access-list |clear |R\d+\()/.test(t);

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

/* ── attempt planning ─────────────────────────────────────────────────── */

/** Domains that actually hold items, with their blueprint weights. */
function availableDomains() {
  return bank.domains
    .map((d) => ({ ...d, have: bank.items.filter((i) => i.domain === d.id).length }))
    .filter((d) => d.have > 0);
}

/**
 * Largest attempt size the bank can serve while keeping the domain ratios.
 * With a partial bank the weights are renormalised over the domains present,
 * so the ratios still hold among whatever exists.
 */
function maxAttempt(domains) {
  const totalW = domains.reduce((s, d) => s + d.weight_pct, 0);
  return Math.min(...domains.map((d) => Math.floor((d.have * totalW) / d.weight_pct)));
}

/** Allocate `size` across domains by weight, using largest-remainder. */
function allocate(size, domains) {
  const totalW = domains.reduce((s, d) => s + d.weight_pct, 0);
  const raw = domains.map((d) => ({ d, exact: (size * d.weight_pct) / totalW }));
  const alloc = raw.map((r) => ({ d: r.d, n: Math.floor(r.exact), rem: r.exact % 1 }));
  let short = size - alloc.reduce((s, a) => s + a.n, 0);
  alloc.sort((a, b) => b.rem - a.rem);
  for (let i = 0; short > 0; i = (i + 1) % alloc.length, short--) alloc[i].n++;
  const out = {};
  alloc.forEach((a) => { out[a.d.id] = Math.min(a.n, a.d.have); });
  return out;
}

function buildAttempt(size) {
  const domains = availableDomains();
  const plan = allocate(size, domains);
  let picked = [];
  for (const d of domains) {
    const pool = shuffle(bank.items.filter((i) => i.domain === d.id));
    picked = picked.concat(pool.slice(0, plan[d.id]));
  }
  return shuffle(picked).map((item) => ({
    item,
    options: shuffle(item.options),   // display order is randomised per attempt
    chosen: null,
  }));
}

/* ── start screen ─────────────────────────────────────────────────────── */

async function init() {
  try {
    const res = await fetch('bank.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    bank = await res.json();
  } catch (err) {
    const isFile = location.protocol === 'file:';
    const note = $('load-status');
    note.className = 'notice notice-warn';
    note.innerHTML = isFile
      ? 'This page needs to be served over HTTP so it can read <code>bank.json</code>. ' +
        'From the repository root run <code>python3 -m http.server -d app 8000</code> ' +
        'and open <code>http://localhost:8000</code>.'
      : `Could not load <code>bank.json</code> (${err.message}). ` +
        'Run <code>python3 scripts/build_bank.py --allow-partial</code> to generate it.';
    return;
  }

  $('bar-ver').textContent = bank.blueprint_version;
  $('load-status').hidden = true;
  $('start-body').hidden = false;

  const rows = $('bank-rows');
  for (const d of bank.domains) {
    const have = Number(bank.counts.per_domain[String(d.id)] || 0);
    const tr = el('tr');
    tr.appendChild(el('td', null, `${d.id}.0  ${d.name}`));
    tr.appendChild(el('td', null, `${d.weight_pct}%`));
    const c = el('td', have ? 'num' : 'num dim', String(have));
    tr.appendChild(c);
    tr.appendChild(el('td', 'num dim', String(d.items_per_100)));
    rows.appendChild(tr);
  }

  const domains = availableDomains();
  const cap = maxAttempt(domains);
  const sel = $('length');

  if (!bank.complete) {
    const missing = bank.domains.filter((d) => !bank.counts.per_domain[String(d.id)]);
    const note = $('partial-note');
    note.hidden = false;
    note.innerHTML =
      `<strong>Partial bank.</strong> ${missing.length} of 6 domains have no items yet ` +
      `(${missing.map((d) => d.id + '.0').join(', ')}), so a full 100-question exam at ` +
      `blueprint quotas is not possible. Attempts below are drawn from the ` +
      `${domains.length === 1 ? 'one domain' : domains.length + ' domains'} that exist, ` +
      `keeping the ratios between them.`;
  }

  const sizes = [...new Set([10, 25, 50, 75, 100, cap].filter((n) => n > 0 && n <= cap))]
    .sort((a, b) => a - b);
  for (const n of sizes) {
    const mins = Math.round(n * MIN_PER_Q);
    const full = bank.complete && n === 100;
    const o = el('option', null,
      `${n} question${n === 1 ? '' : 's'} — ${mins} min${full ? '  (full exam)' : ''}`);
    o.value = String(n);
    sel.appendChild(o);
  }
  sel.value = String(sizes.includes(100) ? 100 : sizes[sizes.length - 1]);
  updateHint();
  sel.addEventListener('change', updateHint);
  $('begin').addEventListener('click', begin);
}

function updateHint() {
  const n = Number($('length').value);
  const mins = Math.round(n * MIN_PER_Q);
  $('setup-hint').textContent =
    `${mins} minutes for ${n} questions, the same ${MIN_PER_Q} minutes per question ` +
    `the real exam allows. The clock does not pause.`;
}

/* ── running the attempt ──────────────────────────────────────────────── */

function show(name) {
  for (const s of ['start', 'exam', 'results']) $(`screen-${s}`).hidden = s !== name;
}

function begin() {
  const size = Number($('length').value);
  const questions = buildAttempt(size);
  run = {
    questions,
    i: 0,
    startedAt: Date.now(),
    limitMs: size * MIN_PER_Q * 60 * 1000,
  };

  $('progress').hidden = false;
  $('timer').hidden = false;
  show('exam');
  window.addEventListener('beforeunload', guard);
  tick = setInterval(updateTimer, 250);
  updateTimer();
  render();
}

function guard(e) { if (run) { e.preventDefault(); e.returnValue = ''; } }

function updateTimer() {
  if (!run) return;
  const left = (run.limitMs - (Date.now() - run.startedAt)) / 1000;
  $('timer-val').textContent = clock(left);
  const t = $('timer');
  t.classList.toggle('is-low', left <= LOW_AT && left > CRIT_AT);
  t.classList.toggle('is-crit', left <= CRIT_AT);
  if (left <= 0) finish(true);
}

function render() {
  const q = run.questions[run.i];
  const it = q.item;
  const obj = bank.objectives[it.objective];

  $('progress').textContent = `Question ${run.i + 1} of ${run.questions.length}`;
  $('q-objective').textContent = `${it.objective}  ${obj ? obj.text : ''}`;
  $('q-stem').textContent = it.stem;

  const fig = $('q-exhibit');
  if (it.exhibit && it.exhibit.kind !== 'none') {
    const kinds = { cli_output: 'CLI output', config: 'Configuration', topology: 'Topology' };
    $('q-exhibit-kind').textContent = kinds[it.exhibit.kind] || 'Exhibit';
    $('q-exhibit-body').textContent = it.exhibit.content;
    fig.hidden = false;
    $('q-exhibit-body').scrollLeft = 0;
  } else {
    fig.hidden = true;
  }

  const multi = it.select_count > 1;
  $('q-legend').textContent = multi ? `Choose ${it.select_count}.` : 'Choose one.';

  const box = $('q-options');
  box.textContent = '';
  q.options.forEach((opt, idx) => {
    const key = String.fromCharCode(65 + idx);
    const label = el('label', 'opt');
    const input = document.createElement('input');
    input.type = multi ? 'checkbox' : 'radio';
    input.name = 'answer';
    input.value = opt.id;                        // original id, not display letter
    input.addEventListener('change', onPick);
    const face = el('div', 'opt-face');
    face.appendChild(el('span', 'opt-key', key));
    const txt = el('span', 'opt-text', opt.text);
    if (looksLikeCommand(opt.text)) txt.classList.add('is-cmd');
    face.appendChild(txt);
    label.append(input, face);
    box.appendChild(label);
  });

  $('confirm').disabled = true;
  $('confirm-hint').textContent = multi
    ? `Select ${it.select_count}. This cannot be undone.`
    : 'This cannot be undone.';
  window.scrollTo(0, 0);
  const first = box.querySelector('input');
  if (first) first.focus();
}

function picked() {
  return [...document.querySelectorAll('#q-options input:checked')].map((i) => i.value);
}

function onPick() {
  const need = run.questions[run.i].item.select_count;
  const got = picked();
  if (got.length > need) {
    // keep the selection honest for multi-answer items
    const inputs = [...document.querySelectorAll('#q-options input:checked')];
    inputs[0].checked = false;
  }
  $('confirm').disabled = picked().length !== need;
}

function confirmAnswer(e) {
  e.preventDefault();
  const q = run.questions[run.i];
  const got = picked();
  if (got.length !== q.item.select_count) return;

  q.chosen = got.slice().sort();
  const key = q.item.correct.slice().sort();
  q.right = q.chosen.length === key.length && q.chosen.every((v, n) => v === key[n]);

  if (run.i + 1 >= run.questions.length) finish(false);
  else { run.i++; render(); }
}

/* ── results ──────────────────────────────────────────────────────────── */

function finish(expired) {
  clearInterval(tick);
  tick = null;
  const elapsed = Math.min(run.limitMs, Date.now() - run.startedAt) / 1000;

  const answered = run.questions.filter((q) => q.chosen !== null);
  const correct = answered.filter((q) => q.right).length;
  const total = run.questions.length;

  const byDomain = {};
  const byObjective = {};
  for (const q of run.questions) {
    const d = String(q.item.domain);
    const o = q.item.objective;
    (byDomain[d] ||= { correct: 0, total: 0 }).total++;
    (byObjective[o] ||= { correct: 0, total: 0 }).total++;
    if (q.right) { byDomain[d].correct++; byObjective[o].correct++; }
  }

  run.report = {
    timestamp: new Date().toISOString(),
    duration: Math.round(elapsed),
    score: { correct, total, percent: pct(correct, total) },
    per_domain: Object.fromEntries(Object.entries(byDomain).map(([k, v]) =>
      [k, { ...v, percent: pct(v.correct, v.total) }])),
    per_objective: Object.fromEntries(Object.entries(byObjective).map(([k, v]) =>
      [k, { ...v, percent: pct(v.correct, v.total) }])),
    missed: run.questions.filter((q) => !q.right).map((q) => ({
      item_id: q.item.id,
      objective: q.item.objective,
      chosen: q.chosen,                 // null when the clock ran out first
      correct: q.item.correct.slice().sort(),
    })),
  };

  window.removeEventListener('beforeunload', guard);
  paintResults(expired);
  const finished = run;
  run = null;                            // attempt is over; timer stops updating
  $('timer').hidden = true;
  $('progress').hidden = true;
  window.__attempt = finished;           // handy when poking at it in the console
  show('results');
  window.scrollTo(0, 0);
}

function paintResults(expired) {
  const r = run.report;
  $('r-pct').textContent = `${r.score.percent}%`;
  $('r-frac').textContent = `${r.score.correct} of ${r.score.total} correct` +
    (expired ? ' — time expired' : '');
  $('r-elapsed').textContent = clock(r.duration);
  $('r-finished').textContent = new Date(r.timestamp).toLocaleString();

  const dRows = $('r-domains');
  dRows.textContent = '';
  for (const d of bank.domains) {
    const s = r.per_domain[String(d.id)];
    if (!s) continue;
    const tr = el('tr');
    tr.appendChild(el('td', null, `${d.id}.0  ${d.name}`));
    tr.appendChild(el('td', 'num', String(s.total)));
    tr.appendChild(el('td', 'num dim', String(d.items_per_100)));
    tr.appendChild(el('td', 'num', String(s.correct)));
    tr.appendChild(rateCell(s.percent));
    dRows.appendChild(tr);
  }

  const oRows = $('r-objectives');
  oRows.textContent = '';
  for (const id of Object.keys(r.per_objective).sort(byObjectiveId)) {
    const s = r.per_objective[id];
    const obj = bank.objectives[id];
    const tr = el('tr');
    tr.appendChild(el('td', null, `${id}  ${obj ? obj.text : ''}`));
    tr.appendChild(el('td', 'num', String(s.total)));
    tr.appendChild(el('td', 'num', String(s.correct)));
    tr.appendChild(rateCell(s.percent));
    oRows.appendChild(tr);
  }

  const missedBox = $('r-missed');
  missedBox.textContent = '';
  const missedQs = run.questions.filter((q) => !q.right);
  $('r-missed-head').textContent = `Missed items (${missedQs.length})`;
  if (!missedQs.length) {
    missedBox.appendChild(el('p', 'all-correct', 'Nothing missed. Every item correct.'));
    return;
  }
  for (const q of missedQs) missedBox.appendChild(missedCard(q));
}

function byObjectiveId(a, b) {
  const [ad, an] = a.split('.').map(Number);
  const [bd, bn] = b.split('.').map(Number);
  return ad - bd || an - bn;
}

function rateCell(p) {
  const td = el('td');
  const meter = el('span', 'meter');
  const fill = el('span');
  fill.style.width = `${p}%`;
  meter.appendChild(fill);
  td.appendChild(meter);
  td.appendChild(document.createTextNode(`${p}%`));
  return td;
}

function missedCard(q) {
  const it = q.item;
  const card = el('div', 'missed');

  const head = el('div', 'missed-head');
  head.appendChild(el('span', null, it.id));
  head.appendChild(el('span', null, `objective ${it.objective}`));
  head.appendChild(el('span', null, `difficulty ${it.difficulty}`));
  if (it.skills && it.skills.length) head.appendChild(el('span', null, it.skills.join(' · ')));
  card.appendChild(head);

  card.appendChild(el('p', 'stem', it.stem));

  if (it.exhibit && it.exhibit.kind !== 'none') {
    const fig = el('figure', 'exhibit');
    const kinds = { cli_output: 'CLI output', config: 'Configuration', topology: 'Topology' };
    fig.appendChild(el('figcaption', null, kinds[it.exhibit.kind] || 'Exhibit'));
    fig.appendChild(el('pre', null, it.exhibit.content));
    card.appendChild(fig);
  }

  const list = el('ul', 'answer-list');
  const chosen = q.chosen || [];
  for (const opt of q.options) {
    const isRight = it.correct.includes(opt.id);
    const wasChosen = chosen.includes(opt.id);
    const li = el('li');
    if (isRight) li.classList.add('is-correct');
    else if (wasChosen) li.classList.add('is-chosen-wrong');
    const mark = isRight ? (wasChosen ? 'correct ✓' : 'correct') : (wasChosen ? 'you ✗' : '');
    li.appendChild(el('span', 'mark', mark));
    const t = el('span', null, opt.text);
    if (looksLikeCommand(opt.text)) t.style.fontFamily = 'var(--mono)';
    li.appendChild(t);
    list.appendChild(li);
  }
  card.appendChild(list);
  card.appendChild(el('p', 'explanation', it.explanation));
  return card;
}

/* ── export ───────────────────────────────────────────────────────────── */

function report() { return (window.__attempt || {}).report; }

function downloadJSON() {
  const r = report();
  if (!r) return;
  const blob = new Blob([JSON.stringify(r, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ccna-attempt-${r.timestamp.replace(/[:.]/g, '-')}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function markdown() {
  const r = report();
  const L = [];
  L.push(`# CCNA 200-301 ${bank.blueprint_version} practice attempt`);
  L.push('');
  L.push(`- **Score:** ${r.score.correct}/${r.score.total} (${r.score.percent}%)`);
  L.push(`- **Elapsed:** ${clock(r.duration)}`);
  L.push(`- **Finished:** ${r.timestamp}`);
  L.push('');
  L.push('## By domain');
  L.push('');
  L.push('| Domain | Asked | Correct | Rate |');
  L.push('|---|---:|---:|---:|');
  for (const d of bank.domains) {
    const s = r.per_domain[String(d.id)];
    if (s) L.push(`| ${d.id}.0 ${d.name} | ${s.total} | ${s.correct} | ${s.percent}% |`);
  }
  L.push('');
  L.push('## By objective');
  L.push('');
  L.push('| Objective | Asked | Correct | Rate |');
  L.push('|---|---:|---:|---:|');
  for (const id of Object.keys(r.per_objective).sort(byObjectiveId)) {
    const s = r.per_objective[id];
    const o = bank.objectives[id];
    L.push(`| ${id} ${o ? o.text : ''} | ${s.total} | ${s.correct} | ${s.percent}% |`);
  }
  if (r.missed.length) {
    L.push('');
    L.push(`## Missed (${r.missed.length})`);
    L.push('');
    for (const m of r.missed) {
      L.push(`- \`${m.item_id}\` (${m.objective}) — chose ` +
        `${m.chosen ? m.chosen.join('+') : 'nothing'}, correct ${m.correct.join('+')}`);
    }
  }
  return L.join('\n');
}

async function copyMarkdown() {
  const text = markdown();
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  }
  const flag = $('copied');
  flag.hidden = false;
  setTimeout(() => { flag.hidden = true; }, 1800);
}

/* ── keyboard ─────────────────────────────────────────────────────────── */

document.addEventListener('keydown', (e) => {
  if (!run || $('screen-exam').hidden) return;
  if (e.target.tagName === 'BUTTON' && e.key === 'Enter') return;

  const inputs = [...document.querySelectorAll('#q-options input')];
  const k = e.key.toUpperCase();
  let idx = -1;
  if (/^[1-9]$/.test(e.key)) idx = Number(e.key) - 1;
  else if (/^[A-E]$/.test(k)) idx = k.charCodeAt(0) - 65;

  if (idx >= 0 && idx < inputs.length) {
    e.preventDefault();
    const input = inputs[idx];
    if (input.type === 'checkbox') input.checked = !input.checked;
    else input.checked = true;
    onPick();
    input.focus();
  } else if (e.key === 'Enter' && !$('confirm').disabled) {
    e.preventDefault();
    $('q-form').requestSubmit();
  }
});

/* ── wiring ───────────────────────────────────────────────────────────── */

$('q-form').addEventListener('submit', confirmAnswer);
$('dl-json').addEventListener('click', downloadJSON);
$('cp-md').addEventListener('click', copyMarkdown);
$('restart').addEventListener('click', () => { location.reload(); });

init();
