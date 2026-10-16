'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const E = require('../app/engine.js');
const { single, multi, dnd, miniBank, seeded } = require('./fixtures.js');

const clone = (o) => JSON.parse(JSON.stringify(o));
const realBank = () => JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'app', 'bank.json'), 'utf8'));

/* ── grading ──────────────────────────────────────────────────────────── */

test('single: only the key is right', () => {
  assert.equal(E.grade(single, ['C']), true);
  assert.equal(E.grade(single, ['A']), false);
  assert.equal(E.grade(single, []), false);
  assert.equal(E.grade(single, null), false);
});

test('multi: all or nothing, order does not matter', () => {
  assert.equal(E.grade(multi, ['D', 'B']), true);
  assert.equal(E.grade(multi, ['B', 'C']), false, 'one right, one wrong');
  assert.equal(E.grade(multi, ['B']), false, 'incomplete');
  assert.equal(E.grade(multi, ['B', 'D', 'A']), false, 'too many');
  assert.equal(E.grade(multi, ['B', 'B']), false, 'a duplicate is not two answers');
});

test('multi: feedback marks chosen, wrong and missed options', () => {
  assert.deepEqual(E.optionMarks(multi, ['B', 'C']),
    { A: 'dim', B: 'correct', C: 'wrong', D: 'missed', E: 'dim' });
});

test('draganddrop: every target must hold its key', () => {
  assert.equal(E.grade(dnd, { T1: 'B', T2: 'A', T3: 'D' }), true);
  assert.equal(E.grade(dnd, { T1: 'B', T2: 'A', T3: 'C' }), false, 'one target wrong');
  assert.equal(E.grade(dnd, { T1: 'B', T2: 'A' }), false, 'a target left empty');
  assert.equal(E.grade(dnd, { T1: 'B', T2: 'A', T3: '' }), false, 'an empty selection');
  assert.equal(E.grade(dnd, ['A', 'B', 'D']), false, 'array is not a dnd answer');
  assert.deepEqual(E.targetMarks(dnd, { T1: 'B', T2: 'C', T3: 'D' }),
    { T1: 'correct', T2: 'wrong', T3: 'correct' });
  assert.equal(E.needed(dnd), 3);
});

test('answer is final and refuses incomplete responses', () => {
  const st = E.buildPractice(miniBank, { ids: [multi.id, dnd.id] });
  assert.equal(E.answer(miniBank, st, 0, ['B']), false);
  assert.equal(st.questions[0].response, null);
  assert.equal(E.answer(miniBank, st, 0, ['D', 'B']), true);
  assert.deepEqual(st.questions[0].response, ['B', 'D']);
  assert.equal(st.questions[0].right, true);
  assert.equal(E.answer(miniBank, st, 0, ['A', 'C']), false, 'no re-answering');
  assert.equal(st.questions[0].right, true);
  assert.equal(E.answer(miniBank, st, 1, { T1: 'B', T2: 'A', T3: 'C' }), true);
  assert.equal(st.questions[1].right, false);
  assert.equal(E.answer(miniBank, st, 7, ['A']), false, 'out of range');
});

/* ── selection ────────────────────────────────────────────────────────── */

test('allocate: blueprint weights hold exactly at 100', () => {
  const bank = realBank();
  const plan = E.allocate(100, E.availableDomains(bank));
  assert.deepEqual(plan, { 1: 20, 2: 20, 3: 25, 4: 10, 5: 15, 6: 10 });
});

test('allocate: largest remainder sums to the size', () => {
  const bank = realBank();
  for (const n of [10, 25, 50, 75, 100]) {
    const plan = E.allocate(n, E.availableDomains(bank));
    assert.equal(Object.values(plan).reduce((a, b) => a + b, 0), n, `size ${n}`);
  }
});

test('buildExam: domain quotas, unique items, 120 minutes for 100', () => {
  const bank = realBank();
  const st = E.buildExam(bank, 100, { rng: seeded(1), now: 1000 });
  const ids = st.questions.map((q) => q.id);
  assert.equal(new Set(ids).size, 100);
  const byId = E.indexBank(bank);
  const per = {};
  for (const id of ids) { const d = byId.get(id).domain; per[d] = (per[d] || 0) + 1; }
  assert.deepEqual(per, { 1: 20, 2: 20, 3: 25, 4: 10, 5: 15, 6: 10 });
  assert.equal(st.limitMs, 120 * 60 * 1000);
  assert.equal(st.mode, 'exam');
});

test('buildExam: three consecutive exams share no item, the fourth repeats the oldest', () => {
  const bank = realBank();
  let seen = {};
  const used = [];
  for (let n = 0; n < 3; n++) {
    const st = E.buildExam(bank, 100, { seen, rng: seeded(10 + n), now: (n + 1) * 1000 });
    used.push(new Set(st.questions.map((q) => q.id)));
    seen = E.markSeen(seen, st);
  }
  for (let a = 0; a < 3; a++) {
    for (let b = a + 1; b < 3; b++) {
      const overlap = [...used[a]].filter((id) => used[b].has(id));
      assert.equal(overlap.length, 0, `exam ${a + 1} vs ${b + 1}`);
    }
  }
  assert.equal(new Set([...used[0], ...used[1], ...used[2]]).size, 300, 'whole bank used');
  const fourth = E.buildExam(bank, 100, { seen, rng: seeded(99), now: 5000 });
  assert.ok(fourth.questions.every((q) => used[0].has(q.id)), 'oldest exam is reused first');
});

test('buildExam shuffles options; buildPractice keeps bank order', () => {
  const bank = realBank();
  const exam = E.buildExam(bank, 100, { rng: seeded(3) });
  const byId = E.indexBank(bank);
  const moved = exam.questions.filter((q) =>
    q.order.join() !== byId.get(q.id).options.map((o) => o.id).join()).length;
  assert.ok(moved > 50, `exam should shuffle options (moved ${moved})`);
  const prac = E.buildPractice(bank, { shuffleOrder: true, rng: seeded(3) });
  assert.ok(prac.questions.every((q) =>
    q.order.join() === byId.get(q.id).options.map((o) => o.id).join()));
  assert.equal(prac.limitMs, null);
});

test('buildPractice: filters combine, empty means all, ids override', () => {
  const bank = realBank();
  assert.equal(E.buildPractice(bank).questions.length, 300);
  const d3 = E.buildPractice(bank, { domains: [3] });
  assert.equal(d3.questions.length, 75);
  const hard34 = E.buildPractice(bank, { objectives: ['3.4'], difficulties: [3] });
  const byId = E.indexBank(bank);
  assert.ok(hard34.questions.length > 0);
  assert.ok(hard34.questions.every((q) => byId.get(q.id).objective === '3.4' && byId.get(q.id).difficulty === 3));
  const picked = E.buildPractice(bank, { ids: ['1.1-001', 'nope', '3.4-002'] });
  assert.deepEqual(picked.questions.map((q) => q.id), ['1.1-001', '3.4-002']);
});

/* ── navigation and time ──────────────────────────────────────────────── */

test('canGoTo: practice anywhere, exam only the current question', () => {
  const p = E.buildPractice(miniBank);
  assert.equal(E.canGoTo(p, 2), true);
  assert.equal(E.canGoTo(p, 3), false);
  const x = E.buildExam(miniBank, 2, { rng: seeded(1) });
  x.pos = 1;
  assert.equal(E.canGoTo(x, 0), false, 'no back');
  assert.equal(E.canGoTo(x, 1), true);
});

test('timer runs on wall clock and finish caps at the limit', () => {
  const x = E.buildExam(miniBank, 2, { rng: seeded(1), now: 0 });
  assert.equal(E.remainingMs(x, 60000), x.limitMs - 60000);
  E.finish(x, x.limitMs + 999999, true);
  assert.equal(x.finishedAt, x.limitMs);
  assert.equal(x.expired, true);
  assert.equal(E.remainingMs(E.buildPractice(miniBank), 1e12), Infinity);
});

/* ── aggregation and report ───────────────────────────────────────────── */

function playedMini(mode) {
  const st = mode === 'exam'
    ? E.buildExam(miniBank, 3, { rng: seeded(2), now: 0 })
    : E.buildPractice(miniBank, { now: 0 });
  const idx = (id) => st.questions.findIndex((q) => q.id === id);
  E.answer(miniBank, st, idx(single.id), ['C']);              // right
  E.answer(miniBank, st, idx(multi.id), ['B', 'C']);          // wrong
  E.toggleFlag(st, idx(single.id));
  E.finish(st, 90000);
  return st;
}

test('summarize: exam counts unanswered as wrong, practice skips them', () => {
  const ex = E.summarize(miniBank, playedMini('exam'));
  assert.deepEqual([ex.correct, ex.total, ex.unanswered], [1, 3, 1]);
  const pr = E.summarize(miniBank, playedMini('practice'));
  assert.deepEqual([pr.correct, pr.total, pr.unanswered], [1, 2, 1]);
  assert.equal(pr.percent, 50);
  assert.deepEqual(pr.per_domain['1'], { correct: 1, total: 2, percent: 50 });
  assert.deepEqual(pr.per_difficulty['2'], { correct: 0, total: 1, percent: 0 });
  assert.equal(pr.per_skill.alpha.wrong, 1);
  assert.equal(pr.flagged, 1);
});

test('weakestFirst sorts ascending and marks below 70 as weak', () => {
  const rows = E.weakestFirst({ '1': { correct: 9, total: 10, percent: 90 },
    '2': { correct: 6, total: 10, percent: 60 }, '3': { correct: 7, total: 10, percent: 70 } });
  assert.deepEqual(rows.map((r) => [r.id, r.weak]), [['2', true], ['3', false], ['1', false]]);
});

test('topMissedSkills ignores single misses', () => {
  const s = { per_skill: {
    a: { wrong: 3, total: 4, domain: 1 }, b: { wrong: 1, total: 1, domain: 1 },
    c: { wrong: 2, total: 2, domain: 2 } } };
  assert.deepEqual(E.topMissedSkills(s).map((x) => x.skill), ['a', 'c']);
  assert.deepEqual(E.topMissedSkills(s, 2).map((x) => x.skill), ['c']);
});

test('report keeps the v1 JSON fields and adds the v2 ones', () => {
  const r = E.report(miniBank, playedMini('exam'));
  for (const k of ['timestamp', 'duration', 'score', 'per_domain', 'per_objective', 'missed', 'unsure_correct']) {
    assert.ok(k in r, `v1 field ${k}`);
  }
  for (const k of ['correct', 'total', 'percent', 'marked_unsure']) assert.ok(k in r.score);
  assert.equal(r.mode, 'exam');
  assert.equal(r.duration, 90);
  assert.equal(r.score.marked_unsure, 1);
  assert.deepEqual(r.unsure_correct.map((u) => u.item_id), [single.id]);
  const unanswered = r.missed.find((m) => m.item_id === dnd.id);
  assert.equal(unanswered.chosen, null);
  assert.deepEqual(unanswered.correct, dnd.correct);
});

test('markdown starts with frontmatter listing missed objectives', () => {
  const md = E.markdown(miniBank, E.report(miniBank, playedMini('exam')));
  const fm = md.split('---\n')[1];
  assert.match(md, /^---\n/);
  assert.match(fm, /^mode: exam$/m);
  assert.match(fm, /^score: 1\/3$/m);
  assert.match(fm, /^missed_objectives: \["1\.1", "2\.1"\]$/m);
  assert.match(md, /## By domain/);
  assert.match(md, /T1=B, T2=A, T3=D/);
});

/* ── serialisation ────────────────────────────────────────────────────── */

test('serialize/restore round-trips and re-grades from the response', () => {
  const st = playedMini('practice');
  st.finishedAt = null;
  st.pos = 1;
  const text = E.serialize(st);
  const back = E.restore(miniBank, text);
  assert.deepEqual(back, JSON.parse(text));
  const tampered = JSON.parse(text);
  tampered.questions.find((q) => q.id === multi.id).right = true;
  assert.equal(E.restore(miniBank, JSON.stringify(tampered)).questions
    .find((q) => q.id === multi.id).right, false, 'a stored verdict is not trusted');
});

test('restore rejects junk, old versions and unknown items', () => {
  const good = JSON.parse(E.serialize(E.buildPractice(miniBank)));
  assert.equal(E.restore(miniBank, 'not json'), null);
  assert.equal(E.restore(miniBank, 'null'), null);
  assert.equal(E.restore(miniBank, JSON.stringify({ ...good, version: 1 })), null);
  const unknown = clone(good); unknown.questions[0].id = '9.9-999';
  assert.equal(E.restore(miniBank, JSON.stringify(unknown)), null);
  const badPos = clone(good); badPos.pos = 99;
  assert.equal(E.restore(miniBank, JSON.stringify(badPos)), null);
  const badResp = clone(good); badResp.questions[1].response = ['A'];
  assert.equal(E.restore(miniBank, JSON.stringify(badResp)), null);
});

test('historyEntry keeps date, mode, score and per-domain percent', () => {
  const h = E.historyEntry(E.report(miniBank, playedMini('exam')));
  assert.deepEqual(Object.keys(h).sort(), ['correct', 'mode', 'per_domain', 'percent', 'timestamp', 'total']);
  assert.deepEqual(h.per_domain, { 1: 50, 2: 0 });
});
