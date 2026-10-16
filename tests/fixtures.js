'use strict';
/* Small synthetic items for engine tests. The real bank has no draganddrop
 * items, so DnD grading is tested here and only here. */

const opts = (...ids) => ids.map((id) => ({ id, text: `option ${id}` }));

const single = {
  id: '1.1-901', objective: '1.1', domain: 1, type: 'single', select_count: 1,
  stem: 'Refer to the exhibit. Single.', exhibit: { kind: 'cli_output', content: 'R1#' },
  options: opts('A', 'B', 'C', 'D'), correct: ['C'],
  explanation: 'x', difficulty: 1, skills: ['alpha', 'beta'],
};

const multi = {
  id: '1.1-902', objective: '1.1', domain: 1, type: 'multi', select_count: 2,
  stem: 'Refer to the exhibit. Which two? (Choose two.)', exhibit: { kind: 'config', content: '!' },
  options: opts('A', 'B', 'C', 'D', 'E'), correct: ['B', 'D'],
  explanation: 'x', difficulty: 2, skills: ['alpha'],
};

const dnd = {
  id: '2.1-903', objective: '2.1', domain: 2, type: 'draganddrop', select_count: 3,
  stem: 'Refer to the exhibit. Drag each port to its role.', exhibit: { kind: 'topology', content: 'SW1' },
  options: opts('A', 'B', 'C', 'D'),
  targets: [{ id: 'T1', text: 'root port' }, { id: 'T2', text: 'designated' }, { id: 'T3', text: 'blocked' }],
  correct: { T1: 'B', T2: 'A', T3: 'D' },
  explanation: 'x', difficulty: 3, skills: ['beta'],
  note: 'Fixture note.',
};

const miniBank = {
  blueprint_version: 'v1.1',
  domains: [
    { id: 1, name: 'One', weight_pct: 50, items_per_100: 50 },
    { id: 2, name: 'Two', weight_pct: 50, items_per_100: 50 },
  ],
  objectives: { '1.1': { text: 'Obj 1.1', domain: 1 }, '2.1': { text: 'Obj 2.1', domain: 2 } },
  items: [single, multi, dnd],
};

/** Deterministic RNG (mulberry32) so selection tests are repeatable. */
function seeded(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

module.exports = { single, multi, dnd, miniBank, seeded };
