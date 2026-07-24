'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const {
  parseLocalDate,
  addDays,
  toISODate,
  computeChallengeWindow,
  daysLeftInChallenge,
  dayNumberForDate,
} = require('../src/dateUtils');

test('parseLocalDate parses YYYY-MM-DD as local midnight', () => {
  const d = parseLocalDate('2026-03-01');
  assert.equal(d.getFullYear(), 2026);
  assert.equal(d.getMonth(), 2); // 0-indexed
  assert.equal(d.getDate(), 1);
});

test('parseLocalDate returns null for empty or malformed input', () => {
  assert.equal(parseLocalDate(''), null);
  assert.equal(parseLocalDate(undefined), null);
  assert.equal(parseLocalDate('not-a-date'), null);
  assert.equal(parseLocalDate('03/01/2026'), null);
});

test('addDays adds and subtracts calendar days, including month rollover', () => {
  const start = parseLocalDate('2026-01-30');
  assert.equal(toISODate(addDays(start, 3)), '2026-02-02');
  assert.equal(toISODate(addDays(start, -30)), '2025-12-31');
});

test('toISODate zero-pads month and day', () => {
  const d = new Date(2026, 0, 5); // Jan 5 2026
  assert.equal(toISODate(d), '2026-01-05');
});

test('computeChallengeWindow spans 75 inclusive days by default', () => {
  const { start, end } = computeChallengeWindow('2026-01-01');
  assert.equal(toISODate(start), '2026-01-01');
  assert.equal(toISODate(end), '2026-03-16'); // day 75, inclusive
});

test('computeChallengeWindow returns null with no start date', () => {
  assert.equal(computeChallengeWindow(''), null);
});

test('daysLeftInChallenge before the start date returns the full length', () => {
  const today = parseLocalDate('2025-12-25');
  assert.equal(daysLeftInChallenge('2026-01-01', 75, today), 75);
});

test('daysLeftInChallenge on day 1 matches the app\'s KPI math (end minus today)', () => {
  // Mirrors the production app's "Days Left" KPI exactly: on day 1 this
  // reads 74, not 75, because it's computed as (end date - today) in
  // whole days rather than an inclusive day count. Documented here so
  // the behavior is intentional and covered, not an accidental regression.
  const today = parseLocalDate('2026-01-01');
  assert.equal(daysLeftInChallenge('2026-01-01', 75, today), 74);
});

test('daysLeftInChallenge on the last day returns 0', () => {
  const today = parseLocalDate('2026-03-16');
  assert.equal(daysLeftInChallenge('2026-01-01', 75, today), 0);
});

test('daysLeftInChallenge after the window closes returns 0, not negative', () => {
  const today = parseLocalDate('2026-04-01');
  assert.equal(daysLeftInChallenge('2026-01-01', 75, today), 0);
});

test('dayNumberForDate maps today onto the right 1-based day', () => {
  const today = parseLocalDate('2026-01-15');
  assert.equal(dayNumberForDate('2026-01-01', 75, today), 15);
});

test('dayNumberForDate returns null outside the challenge window', () => {
  const before = parseLocalDate('2025-12-31');
  const after = parseLocalDate('2026-03-17');
  assert.equal(dayNumberForDate('2026-01-01', 75, before), null);
  assert.equal(dayNumberForDate('2026-01-01', 75, after), null);
});

test('dayNumberForDate returns null with no start date set', () => {
  assert.equal(dayNumberForDate('', 75, new Date()), null);
});
