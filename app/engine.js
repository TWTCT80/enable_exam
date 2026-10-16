/* CCNA 200-301 v1.1 practice runner: the engine.
 *
 * Pure functions only: no DOM, no storage, no clock reads. Anything random takes
 * an `rng` (default Math.random) so tests can pin it; anything time-dependent
 * takes `now` as an argument.
 *
 * Loaded two ways, so it is a classic script rather than an ES module (Chrome
 * refuses modules over file://):
 *   - in the page by <script src="engine.js">, which sets window.Engine
 *   - in node --test by require('../app/engine.js')
 *
 * An attempt is plain data so it can be serialised as it stands:
 *   { version, mode, startedAt, limitMs, pos, finishedAt, expired,
 *     questions: [{ id, order, response, right, flagged }] }
 * `order` is the display order of option ids. Practice keeps the bank's order,
 * because the explanations name options by bank letter ("Option C is ruled out
 * because…") and practice shows the explanation under the question. Exam
 * shuffles it, as the old runner did; review switches back to bank order.
 */
(function (root) {
  'use strict';

  const STATE_VERSION = 2;
  const MIN_PER_Q = 1.2;          // 100 questions / 120 minutes
  const WEAK_BELOW = 70;          // percent; under this a domain or objective is weak
  const SKILL_MIN_MISSES = 2;     // 601 skills over 300 items: one miss is noise
  const SKILL_TOP = 5;

  /* ── helpers ────────────────────────────────────────────────────────── */

  function shuffle(a, rng = Math.random) {
    const out = a.slice();
    for (let i = out.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }

  function pct(n, d) { return d === 0 ? 0 : Math.round((n / d) * 1000) / 10; }

  function clock(sec) {
    sec = Math.max(0, Math.round(sec));
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    const mm = String(m).padStart(2, '0');
    const ss = String(s).padStart(2, '0');
    return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
  }

  function byObjectiveId(a, b) {
    const [ad, an] = a.split('.').map(Number);
    const [bd, bn] = b.split('.').map(Number);
    return ad - bd || an - bn;
  }

  /** Lookup from item id to item, built once per bank. */
  function indexBank(bank) {
    if (!bank._byId) {
      Object.defineProperty(bank, '_byId', {
        value: new Map(bank.items.map((it) => [it.id, it])),
        enumerable: false,
      });
    }
    return bank._byId;
  }

  /* ── selection ──────────────────────────────────────────────────────── */

  /** Domains that actually hold items, with their blueprint weights. */
  function availableDomains(bank) {
    return bank.domains
      .map((d) => ({ ...d, have: bank.items.filter((i) => i.domain === d.id).length }))
      .filter((d) => d.have > 0);
  }

  /** Largest attempt the bank can serve while keeping the domain ratios. */
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
    alloc.sort((a, b) => b.rem - a.rem || a.d.id - b.d.id);
    for (let i = 0; short > 0; i = (i + 1) % alloc.length, short--) alloc[i].n++;
    const out = {};
    alloc.forEach((a) => { out[a.d.id] = Math.min(a.n, a.d.have); });
    return out;
  }

  /**
   * Exam: domain quotas, and within a domain the items least recently seen in
   * an exam first. `seen` maps item id -> timestamp of the exam that used it;
   * an absent id counts as never seen. Shuffling before the stable sort keeps
   * ties random, so 300 items give three exams with no overlap before any
   * item repeats.
   */
  function buildExam(bank, size, { seen = {}, rng = Math.random, now = 0 } = {}) {
    const domains = availableDomains(bank);
    const plan = allocate(size, domains);
    let picked = [];
    for (const d of domains) {
      const pool = shuffle(bank.items.filter((i) => i.domain === d.id), rng)
        .sort((a, b) => (seen[a.id] || 0) - (seen[b.id] || 0));
      picked = picked.concat(pool.slice(0, plan[d.id]));
    }
    const questions = shuffle(picked, rng).map((it) => newQuestion(it, shuffle(optionIds(it), rng)));
    return newAttempt('exam', questions, now, Math.round(size * MIN_PER_Q * 60 * 1000));
  }

  /**
   * Practice: every item matching the filters, or exactly `ids` when given
   * (the "practise the missed ones" path). Empty filter lists mean "all".
   */
  function buildPractice(bank, {
    domains = [], objectives = [], difficulties = [], ids = null,
    shuffleOrder = false, rng = Math.random, now = 0,
  } = {}) {
    const byId = indexBank(bank);
    let items;
    if (ids) {
      items = ids.map((id) => byId.get(id)).filter(Boolean);
    } else {
      items = bank.items.filter((it) =>
        (!domains.length || domains.includes(it.domain)) &&
        (!objectives.length || objectives.includes(it.objective)) &&
        (!difficulties.length || difficulties.includes(it.difficulty)));
    }
    if (shuffleOrder) items = shuffle(items, rng);
    const questions = items.map((it) => newQuestion(it, optionIds(it)));
    return newAttempt('practice', questions, now, null);
  }

  function optionIds(it) { return it.options.map((o) => o.id); }

  function newQuestion(it, order) {
    return { id: it.id, order, response: null, right: null, flagged: false };
  }

  function newAttempt(mode, questions, now, limitMs) {
    return {
      version: STATE_VERSION, mode, startedAt: now, limitMs, pos: 0,
      finishedAt: null, expired: false, questions,
    };
  }

  /* ── grading ────────────────────────────────────────────────────────── */

  /** How many selections make a complete answer. */
  function needed(it) {
    return it.type === 'draganddrop' ? it.targets.length : it.select_count;
  }

  /**
   * Is `response` a complete answer? single/multi take an array of option ids,
   * draganddrop takes { targetId: optionId }.
   */
  function complete(it, response) {
    if (response == null) return false;
    if (it.type === 'draganddrop') {
      return it.targets.every((t) => typeof response[t.id] === 'string' && response[t.id] !== '');
    }
    return Array.isArray(response) && new Set(response).size === it.select_count;
  }

  /** All or nothing, for every type. */
  function grade(it, response) {
    if (!complete(it, response)) return false;
    if (it.type === 'draganddrop') {
      return it.targets.every((t) => response[t.id] === it.correct[t.id]);
    }
    const got = [...new Set(response)].sort();
    const key = it.correct.slice().sort();
    return got.length === key.length && got.every((v, n) => v === key[n]);
  }

  /**
   * Per-option feedback marks for single/multi:
   *   'correct' chosen and right, 'wrong' chosen and not right,
   *   'missed' right but not chosen, 'dim' neither.
   */
  function optionMarks(it, response) {
    const chosen = new Set(response || []);
    const out = {};
    for (const o of it.options) {
      const right = it.correct.includes(o.id);
      out[o.id] = right ? (chosen.has(o.id) ? 'correct' : 'missed')
        : (chosen.has(o.id) ? 'wrong' : 'dim');
    }
    return out;
  }

  /** Per-target feedback for draganddrop: 'correct' or 'wrong'. */
  function targetMarks(it, response) {
    const out = {};
    for (const t of it.targets) out[t.id] = response && response[t.id] === it.correct[t.id] ? 'correct' : 'wrong';
    return out;
  }

  /* ── running an attempt ─────────────────────────────────────────────── */

  /**
   * Record an answer. Returns false and changes nothing when the answer is
   * incomplete, or when the question is already answered: an answer is final
   * in both modes (practice lets you go back to *look*, not to re-answer).
   */
  function answer(bank, state, idx, response) {
    const q = state.questions[idx];
    const it = q && indexBank(bank).get(q.id);
    if (!it || q.response !== null || state.finishedAt !== null) return false;
    if (!complete(it, response)) return false;
    q.response = it.type === 'draganddrop' ? { ...response } : [...new Set(response)].sort();
    q.right = grade(it, q.response);
    return true;
  }

  function toggleFlag(state, idx) {
    const q = state.questions[idx];
    if (q) q.flagged = !q.flagged;
    return q ? q.flagged : false;
  }

  /** May the user move to question `idx`? Practice: anywhere. Exam: no back. */
  function canGoTo(state, idx) {
    if (idx < 0 || idx >= state.questions.length) return false;
    if (state.mode === 'practice') return true;
    return idx === state.pos;
  }

  function answeredCount(state) {
    return state.questions.filter((q) => q.response !== null).length;
  }

  function remainingMs(state, now) {
    if (state.limitMs == null) return Infinity;
    return state.limitMs - (now - state.startedAt);
  }

  function finish(state, now, expired = false) {
    if (state.finishedAt === null) {
      state.finishedAt = state.limitMs == null ? now : Math.min(now, state.startedAt + state.limitMs);
      state.expired = expired;
    }
    return state;
  }

  /* ── aggregation ────────────────────────────────────────────────────── */

  /**
   * Which questions count toward the score. Exam: all of them, an unanswered
   * question is wrong, as on the real exam. Practice: only what was answered,
   * since skipping around is the point of practice.
   */
  function scored(state) {
    return state.mode === 'exam' ? state.questions : state.questions.filter((q) => q.response !== null);
  }

  function summarize(bank, state) {
    const byId = indexBank(bank);
    const qs = scored(state);
    const tally = () => ({ correct: 0, total: 0 });
    const perDomain = {};
    const perObjective = {};
    const perDifficulty = {};
    const perSkill = {};
    for (const q of qs) {
      const it = byId.get(q.id);
      const keys = [
        [perDomain, String(it.domain)],
        [perObjective, it.objective],
        [perDifficulty, String(it.difficulty)],
      ];
      for (const [bag, k] of keys) {
        (bag[k] ||= tally()).total++;
        if (q.right) bag[k].correct++;
      }
      for (const s of it.skills || []) {
        const e = (perSkill[s] ||= { wrong: 0, total: 0, domain: it.domain, objectives: [] });
        e.total++;
        if (!q.right) e.wrong++;
        if (!e.objectives.includes(it.objective)) e.objectives.push(it.objective);
      }
    }
    const withPct = (bag) => Object.fromEntries(Object.entries(bag).map(([k, v]) =>
      [k, { ...v, percent: pct(v.correct, v.total) }]));
    const correct = qs.filter((q) => q.right).length;
    return {
      correct,
      total: qs.length,
      percent: pct(correct, qs.length),
      unanswered: state.questions.length - answeredCount(state),
      flagged: state.questions.filter((q) => q.flagged).length,
      per_domain: withPct(perDomain),
      per_objective: withPct(perObjective),
      per_difficulty: withPct(perDifficulty),
      per_skill: perSkill,
    };
  }

  /** Rows sorted weakest first; ties go to the larger sample, then by id. */
  function weakestFirst(bag) {
    return Object.entries(bag)
      .map(([id, v]) => ({ id, ...v, weak: v.percent < WEAK_BELOW }))
      .sort((a, b) => a.percent - b.percent || b.total - a.total || byObjectiveId(a.id, b.id));
  }

  /** Objectives below the weak line: what "areas to improve" points at. */
  function weakObjectives(summary) {
    return weakestFirst(summary.per_objective).filter((r) => r.weak);
  }

  /** The skills with most misses, optionally within one domain. */
  function topMissedSkills(summary, domain = null) {
    return Object.entries(summary.per_skill)
      .filter(([, v]) => v.wrong >= SKILL_MIN_MISSES && (domain === null || v.domain === domain))
      .map(([skill, v]) => ({ skill, ...v }))
      .sort((a, b) => b.wrong - a.wrong || a.skill.localeCompare(b.skill))
      .slice(0, SKILL_TOP);
  }

  /* ── report and export ──────────────────────────────────────────────── */

  /**
   * The exported attempt. Every field the v1 runner wrote is kept with the same
   * name and meaning; `mode`, `per_difficulty`, `per_skill` and `unanswered`
   * are additions. "unsure" is the v1 name for what v2 calls flagged.
   */
  function report(bank, state) {
    const byId = indexBank(bank);
    const s = summarize(bank, state);
    const qs = scored(state);
    const sortKey = (r) => (Array.isArray(r) ? r.slice().sort() : r);
    return {
      timestamp: new Date(state.finishedAt ?? state.startedAt).toISOString(),
      duration: Math.round(((state.finishedAt ?? state.startedAt) - state.startedAt) / 1000),
      mode: state.mode,
      expired: state.expired,
      score: {
        correct: s.correct,
        total: s.total,
        percent: s.percent,
        marked_unsure: state.questions.filter((q) => q.flagged).length,
        unanswered: s.unanswered,
      },
      per_domain: s.per_domain,
      per_objective: s.per_objective,
      per_difficulty: s.per_difficulty,
      per_skill: Object.fromEntries(Object.entries(s.per_skill)
        .filter(([, v]) => v.wrong > 0)
        .map(([k, v]) => [k, { wrong: v.wrong, total: v.total }])),
      missed: qs.filter((q) => !q.right).map((q) => {
        const it = byId.get(q.id);
        return {
          item_id: q.id,
          objective: it.objective,
          chosen: q.response === null ? null : sortKey(q.response),
          correct: sortKey(it.correct),
          unsure: Boolean(q.flagged),
        };
      }),
      unsure_correct: qs.filter((q) => q.right && q.flagged).map((q) => ({
        item_id: q.id,
        objective: byId.get(q.id).objective,
        chosen: sortKey(q.response),
      })),
    };
  }

  function fmtResponse(r) {
    if (r === null) return 'nothing';
    if (Array.isArray(r)) return r.join('+');
    return Object.entries(r).map(([t, o]) => `${t}=${o}`).join(', ');
  }

  /**
   * Markdown summary: YAML frontmatter for an Obsidian vault, then the v1
   * runner's body unchanged.
   */
  function markdown(bank, r) {
    const missedObjectives = [...new Set(r.missed.map((m) => m.objective))].sort(byObjectiveId);
    const L = [];
    L.push('---');
    L.push(`date: ${r.timestamp}`);
    L.push(`mode: ${r.mode}`);
    L.push(`score: ${r.score.correct}/${r.score.total}`);
    L.push(`percent: ${r.score.percent}`);
    L.push(`blueprint: "${bank.blueprint_version}"`);
    L.push(`missed_objectives: [${missedObjectives.map((o) => `"${o}"`).join(', ')}]`);
    L.push('tags: [ccna, practice-attempt]');
    L.push('---');
    L.push('');
    L.push(`# CCNA 200-301 ${bank.blueprint_version} practice attempt`);
    L.push('');
    L.push(`- **Mode:** ${r.mode}`);
    L.push(`- **Score:** ${r.score.correct}/${r.score.total} (${r.score.percent}%)`);
    if (r.score.marked_unsure) L.push(`- **Marked unsure:** ${r.score.marked_unsure}`);
    if (r.expired) L.push('- **Time expired**');
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
        L.push(`- \`${m.item_id}\` (${m.objective}) — chose ${fmtResponse(m.chosen)}, ` +
          `correct ${fmtResponse(m.correct)}${m.unsure ? ' _(marked unsure)_' : ''}`);
      }
    }
    if (r.unsure_correct.length) {
      L.push('');
      L.push(`## Correct, but marked unsure (${r.unsure_correct.length})`);
      L.push('');
      for (const u of r.unsure_correct) {
        L.push(`- \`${u.item_id}\` (${u.objective}) — answered ${fmtResponse(u.chosen)}`);
      }
    }
    return L.join('\n') + '\n';
  }

  /** One line of history: enough for the trend on the start screen. */
  function historyEntry(r) {
    return {
      timestamp: r.timestamp,
      mode: r.mode,
      correct: r.score.correct,
      total: r.score.total,
      percent: r.score.percent,
      per_domain: Object.fromEntries(Object.entries(r.per_domain).map(([k, v]) => [k, v.percent])),
    };
  }

  /** Record that an exam used these items, for the non-repeating selection. */
  function markSeen(seen, state) {
    const out = { ...seen };
    for (const q of state.questions) out[q.id] = state.startedAt;
    return out;
  }

  /* ── serialisation ──────────────────────────────────────────────────── */

  function serialize(state) { return JSON.stringify(state); }

  /**
   * Parse a stored attempt and check it against the bank. Anything that does
   * not fit (old version, item no longer in the bank, wrong shape) gives null,
   * so a stale save is dropped rather than half-restored.
   */
  function restore(bank, text) {
    let s;
    try { s = JSON.parse(text); } catch { return null; }
    if (!s || s.version !== STATE_VERSION || !['exam', 'practice'].includes(s.mode)) return null;
    if (!Array.isArray(s.questions) || !s.questions.length) return null;
    if (typeof s.startedAt !== 'number' || !Number.isInteger(s.pos)) return null;
    if (s.pos < 0 || s.pos >= s.questions.length) return null;
    const byId = indexBank(bank);
    for (const q of s.questions) {
      const it = byId.get(q && q.id);
      if (!it || !Array.isArray(q.order)) return null;
      const ids = optionIds(it);
      if (q.order.length !== ids.length || !q.order.every((o) => ids.includes(o))) return null;
      if (q.response !== null && !complete(it, q.response)) return null;
      q.right = q.response === null ? null : grade(it, q.response);   // never trust a stored verdict
      q.flagged = Boolean(q.flagged);
    }
    return s;
  }

  const Engine = {
    STATE_VERSION, MIN_PER_Q, WEAK_BELOW,
    shuffle, pct, clock, byObjectiveId, indexBank,
    availableDomains, maxAttempt, allocate, buildExam, buildPractice,
    needed, complete, grade, optionMarks, targetMarks,
    answer, toggleFlag, canGoTo, answeredCount, remainingMs, finish,
    summarize, weakestFirst, weakObjectives, topMissedSkills,
    report, markdown, historyEntry, markSeen,
    serialize, restore,
  };

  root.Engine = Engine;
  if (typeof module !== 'undefined' && module.exports) module.exports = Engine;
})(typeof window !== 'undefined' ? window : globalThis);
