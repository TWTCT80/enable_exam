/* CCNA 200-301 v1.1 practice runner, v2: rendering, events and keyboard.
 *
 * Two modes over one engine (engine.js, no DOM):
 *   practice  immediate feedback and the explanation under each question, free
 *             movement between questions, filters before start. Options keep the
 *             bank's order so "Option C" in an explanation is the third row.
 *   exam      the v1 runner's rules, unchanged: domain quotas, a clock that
 *             never pauses, a confirmed answer is final, no back, no skip, and
 *             nothing about correctness until the results page. The one
 *             annotation is the flag (F, or U as in v1): it changes no scoring
 *             and only decides what the review explains.
 *
 * Rendering follows the reference GUI: each view is a template string built
 * with esc() and dropped into <main>, then wired up.
 */
'use strict';

(function () {
  const E = window.Engine;
  const bank = window.BANK;
  const app = document.getElementById('app');
  const $ = (id) => document.getElementById(id);

  const LOW_AT = 10 * 60;         // seconds: amber
  const CRIT_AT = 2 * 60;         // red, and the only point anything moves
  const KINDS = { cli_output: 'CLI output', config: 'Configuration', topology: 'Topology' };

  /* ── storage ──────────────────────────────────────────────────────── */
  // In-memory only for now; localStorage arrives with the persistence commit.

  const store = { current: null, history: [], seen: {}, prefs: {} };
  function persist() {}

  /* ── state ────────────────────────────────────────────────────────── */

  let st = null;            // the attempt being run, Engine state
  let pending = null;       // selection on the current question, not yet answered
  let done = null;          // { state, report } of the attempt just finished
  let tick = null;
  let shownPos = -1;        // last question painted; a repaint of the same one keeps the scroll

  const byId = bank ? E.indexBank(bank) : null;
  const itemAt = (i) => byId.get(st.questions[i].id);

  /* ── helpers ──────────────────────────────────────────────────────── */

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /** v1's command test, widened to the prefixes the bank's options actually use. */
  const looksLikeCommand = (t) =>
    /^(ip |ipv6 |no |show |network |standby |router |interface |access-list |clear |switchport |ntp |channel-group |channel-protocol |spanning-tree |service |crypto |transport |login|username |enable |line |vlan |R\d+[#(]|SW\d+[#(])/.test(t);
  const optText = (t) => `<span class="t${looksLikeCommand(t) ? ' code' : ''}">${esc(t)}</span>`;

  const letter = (n) => String.fromCharCode(65 + n);
  const objText = (id) => (bank.objectives[id] ? bank.objectives[id].text : '');
  const domainName = (id) => (bank.domains.find((d) => String(d.id) === String(id)) || {}).name || '';

  function exhibitHtml(it) {
    if (!it.exhibit || it.exhibit.kind === 'none') return '';
    const cap = KINDS[it.exhibit.kind] || 'Exhibit';
    return `<figure class="exhibit"><figcaption>${cap}</figcaption>` +
      `<pre tabindex="0" aria-label="${cap} exhibit, scrolls sideways">${esc(it.exhibit.content)}</pre></figure>`;
  }

  /** Display order for the current question: positional letters A–E. */
  function shown(i) {
    const it = itemAt(i);
    const opts = new Map(it.options.map((o) => [o.id, o]));
    return st.questions[i].order.map((id) => opts.get(id));
  }

  function answerText(it, response) {
    if (response === null) return 'no answer';
    if (it.type === 'draganddrop') {
      return it.targets.map((t) => `${t.text} → ${response[t.id] || '—'}`).join('; ');
    }
    const text = new Map(it.options.map((o) => [o.id, o.text]));
    return response.map((id) => `${id}. ${text.get(id)}`).join('; ');
  }

  function show(html, scroll = true) {
    app.innerHTML = html;
    if (scroll) window.scrollTo(0, 0);
  }

  /* ── home ─────────────────────────────────────────────────────────── */

  function home() {
    stopTimer();
    st = null;
    pending = null;
    if (!bank || !E) {
      show(`<h1>Practice exam</h1><div class="notice warn">The item bank did not load.
        Run <code>python3 scripts/build_bank.py</code> to generate <code>app/bank.js</code>.</div>`);
      return;
    }
    const domains = E.availableDomains(bank);
    const cap = E.maxAttempt(domains);
    const sizes = [...new Set([10, 25, 50, 75, 100, cap].filter((n) => n > 0 && n <= cap))].sort((a, b) => a - b);
    const unseen = bank.items.filter((it) => !store.seen[it.id]).length;
    const saved = store.current;

    const domainChecks = bank.domains.map((d) =>
      `<label class="chk"><input type="checkbox" name="f-dom" value="${d.id}"><span>${d.id}.0 ${esc(d.name)}</span></label>`).join('');
    const objChecks = bank.domains.map((d) => {
      const objs = Object.keys(bank.objectives).filter((o) => bank.objectives[o].domain === d.id).sort(E.byObjectiveId);
      return `<span class="dom-head">${d.id}.0 ${esc(d.name)}</span>` + objs.map((o) =>
        `<label class="chk"><input type="checkbox" name="f-obj" value="${o}"><span>${o} ${esc(objText(o))}</span></label>`).join('');
    }).join('');

    show(`
    <h1>CCNA 200-301<br>practice exam</h1>
    <p class="muted">${bank.counts.total} original items written against Cisco's published ${esc(bank.blueprint_version)}
      exam topics. Every item requires reading an exhibit or doing a calculation.</p>
    ${saved ? resumeHtml(saved) : ''}
    <div class="modes">
      <section class="mode" aria-labelledby="m-exam">
        <h2 id="m-exam">Exam</h2>
        <p>Blueprint domain weights, a clock that does not pause, and no feedback until the end.
          A confirmed answer is final: no back, no skip.</p>
        <label class="field">Length
          <select id="length">${sizes.map((n) => `<option value="${n}"${n === Math.min(100, cap) ? ' selected' : ''}>${n} questions — ${Math.round(n * E.MIN_PER_Q)} min${n === 100 && bank.complete ? ' (full exam)' : ''}</option>`).join('')}</select>
        </label>
        <p class="hint">${unseen} of ${bank.counts.total} items not yet seen in an exam; those are drawn first.
          <kbd>F</kbd> flags an item so the review explains it even if you get it right.</p>
        <div class="grow"></div>
        <div><button class="btn" id="start-exam">Start exam</button></div>
      </section>
      <section class="mode" aria-labelledby="m-prac">
        <h2 id="m-prac">Practice</h2>
        <p>Immediate feedback and the explanation under each question. Move freely between questions.</p>
        <fieldset class="filter"><legend>Domains</legend><div class="filter-list">${domainChecks}</div></fieldset>
        <details><summary class="hint">Objectives</summary>
          <fieldset class="filter"><legend>Objectives</legend><div class="filter-list objs">${objChecks}</div></fieldset>
        </details>
        <fieldset class="filter"><legend>Difficulty</legend><div class="filter-list">
          ${[1, 2, 3].map((d) => `<label class="chk"><input type="checkbox" name="f-diff" value="${d}"><span>${d}</span></label>`).join('')}
        </div></fieldset>
        <label class="chk"><input type="checkbox" id="f-shuffle" checked><span>Shuffle question order</span></label>
        <p class="hint" id="f-count" aria-live="polite"></p>
        <div class="grow"></div>
        <div><button class="btn" id="start-prac">Start practice</button></div>
      </section>
    </div>
    ${historyHtml()}
    <details><summary class="hint">Bank coverage</summary>
      <table class="cats">${bank.domains.map((d) => `<tr><td>${d.id}.0 ${esc(d.name)}</td><td class="n">${d.weight_pct}%</td>
        <td class="n">${bank.counts.per_domain[String(d.id)] || 0} items</td><td class="n">${d.items_per_100}/100</td></tr>`).join('')}</table>
    </details>
    <p class="hint" style="margin-top:14px">Simulations cannot be reproduced honestly here; the
      <a href="lab-tasks.md">Packet Tracer lab tasks</a> cover every configure-and-verify objective.
      Keyboard: <kbd>A</kbd>–<kbd>E</kbd> or <kbd>1</kbd>–<kbd>5</kbd> to answer, <kbd>Enter</kbd> to confirm or go on.</p>`);

    $('start-exam').onclick = () => {
      if (!confirmDiscard()) return;
      const s = E.buildExam(bank, Number($('length').value), { seen: store.seen, now: Date.now() });
      store.seen = E.markSeen(store.seen, s);
      run(s);
    };
    const filters = () => ({
      domains: checked('f-dom').map(Number),
      objectives: checked('f-obj'),
      difficulties: checked('f-diff').map(Number),
    });
    const recount = () => {
      const n = E.buildPractice(bank, filters()).questions.length;
      $('f-count').textContent = `${n} question${n === 1 ? '' : 's'} match.`;
      $('start-prac').disabled = n === 0;
    };
    app.querySelectorAll('.filter input').forEach((i) => { i.onchange = recount; });
    recount();
    $('start-prac').onclick = () => {
      if (!confirmDiscard()) return;
      run(E.buildPractice(bank, { ...filters(), shuffleOrder: $('f-shuffle').checked, now: Date.now() }));
    };
    wireHome();
  }

  const checked = (name) => [...app.querySelectorAll(`input[name="${name}"]:checked`)].map((i) => i.value);

  function confirmDiscard() {
    return !store.current || window.confirm('Discard the unfinished attempt and start a new one?');
  }

  // filled in by the persistence commit
  function resumeHtml() { return ''; }
  function historyHtml() { return ''; }
  function wireHome() {}

  /* ── running ──────────────────────────────────────────────────────── */

  function run(state) {
    st = state;
    pending = null;
    shownPos = -1;
    store.current = st;
    persist();
    if (st.mode === 'exam') {
      window.addEventListener('beforeunload', guard);
      startTimer();
    } else {
      stopTimer();
    }
    quiz();
  }

  function guard(e) { if (st && st.mode === 'exam') { e.preventDefault(); e.returnValue = ''; } }

  function startTimer() {
    stopTimer();
    $('timer').hidden = false;
    tick = setInterval(updateTimer, 250);
    updateTimer();
  }

  function stopTimer() {
    clearInterval(tick);
    tick = null;
    $('timer').hidden = true;
    window.removeEventListener('beforeunload', guard);
  }

  function updateTimer() {
    if (!st || st.mode !== 'exam') return;
    const left = E.remainingMs(st, Date.now()) / 1000;
    $('timer-val').textContent = E.clock(left);
    const t = $('timer');
    t.classList.toggle('is-low', left <= LOW_AT && left > CRIT_AT);
    t.classList.toggle('is-crit', left <= CRIT_AT);
    if (left <= 0) end_(true);
  }

  function portsHtml() {
    const exam = st.mode === 'exam';
    return st.questions.map((q, i) => {
      const cls = ['port'];
      if (exam) {
        if (q.response !== null) cls.push('done');
        if (q.flagged) cls.push('flag');
      } else if (q.response !== null) {
        cls.push(q.right ? 'ok' : 'bad');
      }
      if (i === st.pos) cls.push('cur');
      if (exam) return `<span class="${cls.join(' ')}"></span>`;
      const state = q.response === null ? 'unanswered' : (q.right ? 'correct' : 'wrong');
      return `<button type="button" class="${cls.join(' ')}" data-go="${i}" tabindex="-1" aria-label="Question ${i + 1}, ${state}"></button>`;
    }).join('');
  }

  function quiz() {
    const i = st.pos;
    const q = st.questions[i];
    const it = itemAt(i);
    const exam = st.mode === 'exam';
    const answered = q.response !== null;
    const reveal = answered && !exam;
    const total = st.questions.length;
    const nAns = E.answeredCount(st);
    const nRight = st.questions.filter((x) => x.right).length;
    const last = i === total - 1;
    if (!answered && pending === null) pending = it.type === 'draganddrop' ? {} : [];

    const head = exam
      ? `<span>Answered <b>${nAns}</b> of ${total} · flagged <b>${st.questions.filter((x) => x.flagged).length}</b></span>`
      : `<span>Score: <b>${nRight}</b> / ${nAns}</span>`;
    const legend = exam
      ? `<div class="legend" aria-hidden="true"><span style="--sw:var(--led-off)">unanswered</span>
         <span style="--sw:var(--led-on)">answered</span><span style="--sw:var(--warn)">flagged</span></div>` : '';

    let body;
    if (it.type === 'draganddrop') body = dndHtml(it, q, reveal);
    else body = optionsHtml(it, q, i, exam, reveal);

    let fb = '';
    if (reveal) {
      const keyText = it.type === 'draganddrop' ? 'see the corrections above'
        : `the answer is ${it.correct.join(' and ')}`;
      fb = `<div class="fb ${q.right ? 'ok' : 'bad'}" role="status">
        <h3>${q.right ? 'Correct' : `Wrong — ${keyText}`}</h3><p>${esc(it.explanation)}</p></div>
        ${it.note ? `<div class="fix"><strong>Corrected question.</strong> ${esc(it.note)}</div>` : ''}`;
    }

    const needsSubmit = !answered && (exam || it.type !== 'single');
    const submit = needsSubmit
      ? `<button class="btn" id="submit" disabled>${exam ? 'Confirm answer' : 'Answer'}</button>` : '';
    let nav;
    if (exam) {
      nav = `<div class="nav"><button class="btn ghost" id="end">End exam</button>
        <div class="row"><span class="hint">This cannot be undone.</span>${submit}</div></div>
        <label class="chk flagbox"><input type="checkbox" id="flag" ${q.flagged ? 'checked' : ''}>
          <span>Flag: explain this one afterwards even if I get it right <kbd>F</kbd></span></label>`;
    } else {
      nav = `<div class="nav"><div class="row">
          <button class="btn ghost" id="prev" ${i === 0 ? 'disabled' : ''}>Previous</button>
          <button class="btn ghost" id="end">End and show results</button></div>
        <div class="row">${submit}<button class="btn" id="next" ${answered ? '' : 'disabled'}>${last ? 'Show results' : 'Next question'}</button></div></div>`;
    }

    const keys = exam
      ? 'Keys: A–E or 1–5 to select, Enter to confirm, F to flag.'
      : (it.type === 'draganddrop' ? 'Drag each item onto a target, or pick from the list. Enter to answer, then Enter for next. ← → to move.'
        : `Keys: A–E or 1–5 to ${it.type === 'single' ? 'answer' : 'select'}, Enter for ${it.type === 'single' ? 'next' : 'answer, then next'}. ← → to move.`);

    const moved = shownPos !== i;
    shownPos = i;
    show(`
    <div class="panel">
      <div class="panel-head"><span>Question <b>${i + 1}</b> of ${total}</span>${head}</div>
      <div class="ports" ${exam ? 'aria-hidden="true"' : 'role="group" aria-label="Questions"'}>${portsHtml()}</div>
      ${legend}
    </div>
    <article class="card" aria-labelledby="qtext">
      <div class="qmeta"><span class="tag">${it.objective} ${esc(objText(it.objective))}</span>
        <span>${esc(it.id)} · difficulty ${it.difficulty}</span></div>
      ${exhibitHtml(it)}
      <p class="qtext" id="qtext">${esc(it.stem).replace(/\n/g, '<br>')}</p>
      ${it.type === 'multi' ? `<p class="choose">Choose ${it.select_count}.</p>` : ''}
      ${body}
      ${fb}
      ${nav}
      <p class="hint" style="margin-top:12px">${keys}</p>
    </article>`, moved);

    wireQuiz(it, q, exam, answered);
  }

  function optionsHtml(it, q, i, exam, reveal) {
    const multi = it.type === 'multi';
    const opts = shown(i);
    const marks = reveal ? E.optionMarks(it, q.response) : null;
    const chosen = q.response || pending || [];
    // Practice single: one click answers, as in the reference. Everything else
    // selects first; in the exam that is what keeps a stray key from being final.
    const instant = !exam && !multi;
    const rows = opts.map((o, n) => {
      const key = letter(n);
      const cls = ['opt'];
      if (multi) cls.push('multi');
      let badge = '';
      if (marks) {
        let m = marks[o.id];
        if (!multi && m === 'missed') m = 'correct';     // single: the key is simply green
        cls.push(m);
        if (m === 'missed') badge = '<span class="badge">missed</span>';
      } else if (chosen.includes(o.id)) {
        cls.push('sel');
      }
      if (q.response !== null) cls.push('locked');
      if (instant) {
        return `<button type="button" class="${cls.join(' ')}" data-id="${o.id}" ${q.response !== null ? 'disabled' : ''}>
          <span class="k">${key}</span>${optText(o.text)}${badge}</button>`;
      }
      return `<label class="${cls.join(' ')}"><input type="${multi ? 'checkbox' : 'radio'}" name="ans" value="${o.id}"
          ${chosen.includes(o.id) ? 'checked' : ''} ${q.response !== null ? 'disabled' : ''}>
        <span class="k">${key}</span>${optText(o.text)}${badge}</label>`;
    }).join('');
    const legend = multi ? `Choose ${it.select_count}` : 'Choose one';
    return instant
      ? `<div class="opts" role="group" aria-label="${legend}">${rows}</div>`
      : `<fieldset class="opts"><legend class="sr-only">${legend}</legend>${rows}</fieldset>`;
  }

  function dndHtml(it, q, reveal) {
    const resp = q.response || pending || {};
    const locked = q.response !== null;
    const marks = reveal ? E.targetMarks(it, q.response) : null;
    const byOpt = new Map(it.options.map((o) => [o.id, o]));
    const chips = it.options.map((o) =>
      `<span class="chip" draggable="${locked ? 'false' : 'true'}" data-id="${o.id}"><span class="k">${o.id}</span>${optText(o.text)}</span>`).join('');
    const rows = it.targets.map((t) => {
      const cls = ['target'];
      if (marks) cls.push(marks[t.id]);
      const sel = `<select data-target="${t.id}" aria-label="${esc(t.text)}" ${locked ? 'disabled' : ''}>
        <option value="">— choose —</option>
        ${it.options.map((o) => `<option value="${o.id}" ${resp[t.id] === o.id ? 'selected' : ''}>${o.id}. ${esc(o.text)}</option>`).join('')}
      </select>`;
      const fix = marks && marks[t.id] === 'wrong'
        ? `<span class="fixline">Correct: ${it.correct[t.id]}. ${esc(byOpt.get(it.correct[t.id]).text)}</span>` : '';
      return `<div class="${cls.join(' ')}" data-target="${t.id}"><span>${esc(t.text)}</span>${sel}${fix}</div>`;
    }).join('');
    return `<div class="dnd"><div class="tray" aria-hidden="true">${chips}</div>
      <div class="targets" role="group" aria-label="Targets">${rows}</div></div>`;
  }

  function wireQuiz(it, q, exam, answered) {
    app.querySelectorAll('[data-go]').forEach((b) => { b.onclick = () => go(Number(b.dataset.go)); });
    const end = $('end');
    if (end) end.onclick = () => {
      const left = st.questions.length - E.answeredCount(st);
      if (exam && !window.confirm(`End the exam now? ${left} unanswered question${left === 1 ? '' : 's'} will count as wrong.`)) return;
      end_(false);
    };
    if ($('prev')) $('prev').onclick = () => go(st.pos - 1);
    if ($('next')) $('next').onclick = next;
    if ($('flag')) $('flag').onchange = (e) => { if (e.target.checked !== q.flagged) flag(); };
    if ($('submit')) $('submit').onclick = submit;

    if (!answered) {
      app.querySelectorAll('button.opt').forEach((b) => { b.onclick = () => respond([b.dataset.id]); });
      app.querySelectorAll('.opt input').forEach((inp) => { inp.onchange = () => pick(inp.value, inp.checked); });
      app.querySelectorAll('select[data-target]').forEach((s) => { s.onchange = () => place(s.dataset.target, s.value); });
      wireDrag();
    }
    refreshSubmit();

    // Focus: the first choice on a fresh question, Next once answered.
    const target = answered ? $('next')
      : app.querySelector('button.opt:not([disabled]), .opt input:not([disabled]), select[data-target]:not([disabled])');
    if (target) target.focus({ preventScroll: true });
  }

  /* ── selection and answering ──────────────────────────────────────── */

  function pick(id, on) {
    const it = itemAt(st.pos);
    if (it.type === 'single') pending = [id];
    else {
      pending = pending.filter((x) => x !== id);
      if (on) pending.push(id);
      // keep the selection honest: choosing one too many drops the oldest
      while (pending.length > it.select_count) pending.shift();
    }
    app.querySelectorAll('.opt input').forEach((inp) => {
      inp.checked = pending.includes(inp.value);
      inp.closest('.opt').classList.toggle('sel', inp.checked);
    });
    refreshSubmit();
  }

  function place(target, id) {
    pending = { ...pending, [target]: id };
    if (!id) delete pending[target];
    const s = app.querySelector(`select[data-target="${target}"]`);
    if (s) s.value = id;
    refreshSubmit();
  }

  function refreshSubmit() {
    const b = $('submit');
    if (b) b.disabled = !E.complete(itemAt(st.pos), pending);
  }

  function submit() {
    if (pending !== null) respond(pending);
  }

  function respond(response) {
    if (!E.answer(bank, st, st.pos, response)) return;
    pending = null;
    persist();
    if (st.mode === 'exam') next();      // exam: on to the next question, no verdict
    else quiz();
  }

  function next() {
    if (st.pos < st.questions.length - 1) {
      st.pos++;
      pending = null;
      persist();
      quiz();
    } else {
      end_(false);
    }
  }

  function go(i) {
    if (!E.canGoTo(st, i) || i === st.pos) return;
    st.pos = i;
    pending = null;
    persist();
    quiz();
  }

  function flag() {
    E.toggleFlag(st, st.pos);
    persist();
    const box = $('flag');
    if (box) box.checked = st.questions[st.pos].flagged;
    // repaint only the panel so the selection in progress is kept
    const ports = app.querySelector('.ports');
    if (ports) ports.innerHTML = portsHtml();
    const head = app.querySelector('.panel-head span:last-child b:last-child');
    if (head) head.textContent = st.questions.filter((x) => x.flagged).length;
  }

  /* Drag on desktop. The select in each target is the accessible path and the
   * only one on touch screens; dragging simply sets that select. */
  function wireDrag() {
    app.querySelectorAll('.chip[draggable="true"]').forEach((c) => {
      c.ondragstart = (e) => { e.dataTransfer.setData('text/plain', c.dataset.id); c.classList.add('dragging'); };
      c.ondragend = () => c.classList.remove('dragging');
    });
    app.querySelectorAll('.target').forEach((t) => {
      t.ondragover = (e) => { e.preventDefault(); t.classList.add('over'); };
      t.ondragleave = () => t.classList.remove('over');
      t.ondrop = (e) => {
        e.preventDefault();
        t.classList.remove('over');
        const id = e.dataTransfer.getData('text/plain');
        if (id) place(t.dataset.target, id);
      };
    });
  }

  /* ── ending ───────────────────────────────────────────────────────── */

  function end_(expired) {
    if (!st) return;
    E.finish(st, Date.now(), expired);
    const r = E.report(bank, st);
    if (E.answeredCount(st) > 0 || st.mode === 'exam') {
      store.history = [...store.history, E.historyEntry(r)].slice(-50);
    }
    store.current = null;
    persist();
    done = { state: st, report: r };
    stopTimer();
    st = null;
    pending = null;
    results();
  }

  /* ── results ──────────────────────────────────────────────────────── */

  function results() {
    const { state, report: r } = done;
    const exam = state.mode === 'exam';
    const s = E.summarize(bank, state);
    const pct = s.percent;
    const verdict = s.total === 0 ? 'You have not answered any questions yet.'
      : pct >= 85 ? 'Strong result. Keep revising the areas where you dropped points.'
        : pct >= 70 ? 'A good base, but there are gaps to close before the exam.'
          : 'There are several areas to work on — start with the weakest below.';

    const weak = E.weakObjectives(s);
    const weakShown = weak.slice(0, 8);
    const focus = s.total === 0 ? '' : weak.length
      ? `<div class="focus"><strong>Areas to improve</strong><ul>${weakShown.map((o) =>
        `<li><b>${o.id}</b> ${esc(objText(o.id))} (${o.correct}/${o.total})</li>`).join('')}</ul>
        ${weak.length > weakShown.length ? `<p class="hint" style="margin:6px 0 0">and ${weak.length - weakShown.length} more below 70 %.</p>` : ''}</div>`
      : '<div class="focus good"><strong>No clearly weak areas</strong> — every objective is at 70 % or higher.</div>';

    const domains = E.weakestFirst(s.per_domain).map((d) => {
      const objs = E.weakestFirst(Object.fromEntries(Object.entries(s.per_objective)
        .filter(([o]) => bank.objectives[o] && String(bank.objectives[o].domain) === d.id)));
      const skills = E.topMissedSkills(s, Number(d.id));
      return `<details class="domain${d.weak ? ' weak' : ''}"><summary>
          <span class="name">${d.id}.0 ${esc(domainName(d.id))}</span>
          <div class="bar-m" aria-hidden="true"><i style="width:${d.percent}%"></i></div>
          <span class="n">${d.correct}/${d.total}</span></summary>
        <div class="domain-body">
          <table class="cats">${objs.map((o) => `<tr class="${o.weak ? 'weak' : ''}"><td>${o.id} ${esc(objText(o.id))}</td>
            <td class="barcell"><div class="bar-m" aria-hidden="true"><i style="width:${o.percent}%"></i></div></td>
            <td class="n">${o.correct}/${o.total}</td></tr>`).join('')}</table>
          ${skills.length ? `<p class="skills">Most-missed skills: ${skills.map((k) =>
            `<code>${esc(k.skill)}</code> (${k.wrong} of ${k.total})`).join(', ')}</p>` : ''}
        </div></details>`;
    }).join('');

    const diff = [1, 2, 3].filter((d) => s.per_difficulty[d]).map((d) => {
      const v = s.per_difficulty[d];
      return `<tr class="${v.percent < E.WEAK_BELOW ? 'weak' : ''}"><td>Difficulty ${d}</td>
        <td class="barcell"><div class="bar-m" aria-hidden="true"><i style="width:${v.percent}%"></i></div></td>
        <td class="n">${v.correct}/${v.total}</td></tr>`;
    }).join('');

    const missedIds = r.missed.map((m) => m.item_id);
    const meta = [
      exam ? 'Exam' : 'Practice',
      `elapsed ${E.clock(r.duration)}`,
      new Date(r.timestamp).toLocaleString(),
      s.flagged ? `${s.flagged} flagged` : '',
    ].filter(Boolean).join(' · ');

    show(`
    <h1>${exam ? 'Exam complete' : 'Results'}</h1>
    <div class="score"><span class="big">${s.correct}/${s.total}</span>
      <span class="muted">${pct} % correct${s.unanswered ? ` · ${s.unanswered} ${exam ? 'unanswered' : 'not attempted'}` : ''}${state.expired ? ' · time expired' : ''}</span></div>
    <p class="hint">${meta}</p>
    <p>${verdict} <span class="muted">Cisco publishes no official pass mark; aim for 85 % or more on practice exams.</span></p>
    ${focus}
    <div class="actions">
      ${missedIds.length ? `<button class="btn" id="retry">Practise the ${missedIds.length} missed</button>` : ''}
      <button class="btn ghost" id="again">New attempt</button>
      <button class="btn ghost" id="dl-json">Download JSON</button>
      <button class="btn ghost" id="dl-md">Download Markdown</button>
      <button class="btn ghost" id="cp-md">Copy Markdown</button>
      <span class="copied" id="copied" role="status"></span>
    </div>
    ${s.total ? `<h2>Score by domain</h2><p class="hint">Weakest first; red is below 70 %. Open a domain for its objectives.</p>
    <div class="domains">${domains}</div>
    <h2>By difficulty</h2><table class="cats">${diff}</table>` : ''}
    <h2>All answers</h2>
    ${exam ? `<p class="hint">Options below keep the lettering the explanations use (A first, then B, C…). The exam showed
      them in a random order, so these letters will not match the positions you saw; the marks show what happened.</p>` : ''}
    <div class="row" style="margin-bottom:8px">
      <label class="chk"><input type="checkbox" id="only-wrong"><span>Show only wrong answers</span></label>
      ${exam ? '<label class="chk"><input type="checkbox" id="only-flag"><span>Show only flagged</span></label>' : ''}
    </div>
    <ul class="review" id="rev"></ul>`);

    const draw = () => drawReview(state, $('only-wrong').checked, $('only-flag') ? $('only-flag').checked : false);
    $('only-wrong').onchange = draw;
    if ($('only-flag')) $('only-flag').onchange = draw;
    draw();
    if ($('retry')) $('retry').onclick = () => run(E.buildPractice(bank, { ids: missedIds, shuffleOrder: true, now: Date.now() }));
    $('again').onclick = home;
    $('dl-json').onclick = () => download(JSON.stringify(r, null, 2), 'json', 'application/json');
    $('dl-md').onclick = () => download(E.markdown(bank, r), 'md', 'text/markdown');
    $('cp-md').onclick = () => copy(E.markdown(bank, r));
    app.focus({ preventScroll: true });
  }

  function drawReview(state, onlyWrong, onlyFlag) {
    const rev = $('rev');
    const list = state.questions.map((q, n) => ({ q, n }))
      .filter(({ q }) => (state.mode === 'exam' || q.response !== null) &&
        (!onlyWrong || !q.right) && (!onlyFlag || q.flagged));
    if (!list.length) {
      rev.innerHTML = `<li class="muted">${onlyWrong ? 'No wrong answers — nicely done.' : 'Nothing to show.'}</li>`;
      return;
    }
    rev.innerHTML = list.map(({ q, n }) => {
      const it = byId.get(q.id);
      const you = q.response === null ? 'no answer' : answerText(it, q.response);
      return `<li><div class="q">${n + 1}. ${esc(it.stem).replace(/\n/g, ' · ')}${q.flagged ? '<span class="flag-tag">flagged</span>' : ''}</div>
        <div class="a"><span class="you ${q.right ? 'ok' : 'bad'}">Your answer: ${esc(you)}</span>
        ${q.right ? '' : `<br>Correct answer: ${esc(answerText(it, it.correct))}`}</div>
        <details data-n="${n}"><summary>Explanation</summary><div class="detail"></div></details></li>`;
    }).join('');
    // Built on first open: 100 exhibits are not worth painting up front.
    rev.querySelectorAll('details').forEach((d) => {
      d.ontoggle = () => {
        const box = d.querySelector('.detail');
        if (d.open && !box.childElementCount) box.innerHTML = reviewDetail(state.questions[Number(d.dataset.n)]);
      };
    });
  }

  /** Review detail in the bank's own order, with the bank's letters, because
   *  the explanations name letters ("Option C is ruled out because…"). */
  function reviewDetail(q) {
    const it = byId.get(q.id);
    let answers;
    if (it.type === 'draganddrop') {
      answers = `<ul class="answer-list">${it.targets.map((t) => {
        const got = q.response && q.response[t.id];
        const ok = got === it.correct[t.id];
        return `<li class="${ok ? 'is-correct' : 'is-wrong'}"><span class="mark">${ok ? 'correct' : 'you ✗'}</span>
          <span class="t">${esc(t.text)} → ${got || '—'}${ok ? '' : `, correct ${it.correct[t.id]}`}</span></li>`;
      }).join('')}</ul>`;
    } else {
      const chosen = q.response || [];
      answers = `<ul class="answer-list">${it.options.map((o) => {
        const right = it.correct.includes(o.id);
        const was = chosen.includes(o.id);
        const cls = right ? 'is-correct' : (was ? 'is-wrong' : '');
        const mark = right ? (was ? 'correct ✓' : (it.type === 'multi' && q.response ? 'missed' : 'correct')) : (was ? 'you ✗' : '');
        return `<li class="${cls}"><span class="key">${o.id}</span><span class="mark">${mark}</span>${optText(o.text)}</li>`;
      }).join('')}</ul>`;
    }
    return `${exhibitHtml(it)}${answers}<p>${esc(it.explanation)}</p>
      ${it.note ? `<div class="fix"><strong>Corrected question.</strong> ${esc(it.note)}</div>` : ''}
      <p class="hint">${esc(it.id)} · objective ${it.objective} · difficulty ${it.difficulty} · ${esc((it.skills || []).join(' · '))}</p>`;
  }

  /* ── export ───────────────────────────────────────────────────────── */

  function download(text, ext, type) {
    const r = done.report;
    const blob = new Blob([text], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ccna-attempt-${r.timestamp.replace(/[:.]/g, '-')}.${ext}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function copy(text) {
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
    const flagEl = $('copied');
    flagEl.textContent = 'Copied';
    setTimeout(() => { flagEl.textContent = ''; }, 1800);
  }

  /* ── keyboard ─────────────────────────────────────────────────────── */

  document.addEventListener('keydown', (e) => {
    if (!st || !app.querySelector('.card') || e.metaKey || e.ctrlKey || e.altKey) return;
    const tag = e.target.tagName;
    if (tag === 'SELECT' || tag === 'TEXTAREA') return;
    const q = st.questions[st.pos];
    const it = itemAt(st.pos);
    const exam = st.mode === 'exam';
    const k = e.key.toUpperCase();

    if (exam && (k === 'F' || k === 'U')) { e.preventDefault(); flag(); return; }
    if (!exam && (e.key === 'ArrowLeft' || e.key === 'ArrowRight') && tag !== 'INPUT') {
      e.preventDefault();
      go(st.pos + (e.key === 'ArrowLeft' ? -1 : 1));
      return;
    }

    let idx = -1;
    if (/^[1-9]$/.test(e.key)) idx = Number(e.key) - 1;
    else if (/^[A-E]$/.test(k) && e.key.length === 1) idx = k.charCodeAt(0) - 65;
    if (idx >= 0) {
      const opts = it.type === 'draganddrop' ? [] : shown(st.pos);
      if (q.response !== null || idx >= opts.length) return;
      e.preventDefault();
      const id = opts[idx].id;
      if (!exam && it.type === 'single') respond([id]);
      else {
        pick(id, it.type === 'single' ? true : !pending.includes(id));
        const inp = app.querySelector(`.opt input[value="${id}"]`);
        if (inp) inp.focus();
      }
      return;
    }

    if (e.key === 'Enter') {
      if (tag === 'BUTTON' || tag === 'SUMMARY' || tag === 'A') return;   // native activation
      const sub = $('submit');
      if (sub && !sub.disabled) { e.preventDefault(); submit(); return; }
      const nx = $('next');
      if (nx && !nx.disabled) { e.preventDefault(); next(); }
    }
  });

  /* ── theme ────────────────────────────────────────────────────────── */

  const THEMES = ['auto', 'light', 'dark'];
  function applyTheme(t) {
    if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t;
    else delete document.documentElement.dataset.theme;
    $('theme').textContent = `Theme: ${t}`;
  }
  $('theme').onclick = () => {
    const cur = store.prefs.theme || 'auto';
    store.prefs.theme = THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length];
    persist();
    applyTheme(store.prefs.theme);
  };

  /* ── start ────────────────────────────────────────────────────────── */

  if (bank) $('bar-ver').textContent = bank.blueprint_version;
  applyTheme(store.prefs.theme || 'auto');
  home();
})();
