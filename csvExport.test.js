'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { calcStreak } = require('../src/streak');

const day = (completed) => ({ completed });

test('empty array has zero streak', () => {
  assert.equal(calcStreak([]), 0);
});

test('all completed days gives a streak equal to the array length', () => {
  const days = Array.from({ length: 10 }, () => day(true));
  assert.equal(calcStreak(days), 10);
});

test('a single incomplete day resets the streak to zero', () => {
  const days = [day(true), day(true), day(false)];
  assert.equal(calcStreak(days), 0);
});

test('streak counts only the trailing run of completed days', () => {
  // completed, completed, MISSED, completed, completed, completed
  const days = [day(true), day(true), day(false), day(true), day(true), day(true)];
  assert.equal(calcStreak(days), 3);
});

test('treats missing/undefined day records as incomplete', () => {
  const days = [day(true), undefined, day(true)];
  assert.equal(calcStreak(days), 1);
});
