'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { RULES, isDayComplete } = require('../src/challengeRules');

test('all three challenges are defined with a required list', () => {
  for (const key of ['hard', 'medium', 'soft']) {
    assert.ok(RULES[key], `expected RULES.${key} to exist`);
    assert.ok(Array.isArray(RULES[key].required));
    assert.ok(RULES[key].required.length > 0);
  }
});

test('75 Hard requires all six tasks, including outdoor and photo', () => {
  const allButPhoto = { workouts: true, outdoor: true, diet: true, water: true, reading: true, photo: false };
  assert.equal(isDayComplete('hard', allButPhoto), false);

  const all = { ...allButPhoto, photo: true };
  assert.equal(isDayComplete('hard', all), true);
});

test('75 Medium does not require outdoor or photo', () => {
  const tasks = { workouts: true, diet: true, water: true, reading: true };
  assert.equal(isDayComplete('medium', tasks), true);
  assert.equal(isDayComplete('medium', { ...tasks, water: false }), false);
});

test('75 Soft mirrors Medium\'s required set', () => {
  const tasks = { workouts: true, diet: true, water: true, reading: true };
  assert.equal(isDayComplete('soft', tasks), true);
});

test('missing tasks object is treated as nothing checked', () => {
  assert.equal(isDayComplete('soft'), false);
});

test('isDayComplete throws on an unknown challenge key', () => {
  assert.throws(() => isDayComplete('extreme', {}), /Unknown challenge/);
});
