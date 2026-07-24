'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const {
  bucketDifficulty,
  equipmentBucket,
  filterWorkouts,
  recentIds,
  pickShuffle,
} = require('../src/workoutLibrary');

test('bucketDifficulty trusts an explicit difficulty word first', () => {
  assert.equal(bucketDifficulty('Medium\u2013Hard', 'Low'), 'hard');
  assert.equal(bucketDifficulty('Easy\u2013Medium', 'High'), 'medium');
  assert.equal(bucketDifficulty('Easy', 'High'), 'easy');
});

test('bucketDifficulty falls back to impact when given a workout *type* instead of a difficulty', () => {
  // Real source-data quirk: some rows have a workout type ("HIIT",
  // "Full Body Strength", etc.) in the difficulty column instead of an
  // actual difficulty word.
  assert.equal(bucketDifficulty('HIIT/Strength', 'High'), 'hard');
  assert.equal(bucketDifficulty('Full Body Strength', 'Moderate'), 'medium');
  assert.equal(bucketDifficulty('Cardio', 'Low'), 'easy');
});

test('equipmentBucket recognizes common equipment phrasing', () => {
  assert.equal(equipmentBucket('None'), 'none');
  assert.equal(equipmentBucket('None (opt. light weights)'), 'none');
  assert.equal(equipmentBucket('Dumbbells (optional)'), 'dumbbells');
  assert.equal(equipmentBucket('Long resistance band'), 'band');
  assert.equal(equipmentBucket('Chair (optional)'), 'chair');
  assert.equal(equipmentBucket('Jump rope'), 'other');
});

const FIXTURE_WORKOUTS = [
  { id: 1, section: 'yoga', difficulty: 'easy', equipment: 'None' },
  { id: 2, section: 'yoga', difficulty: 'medium', equipment: 'None' },
  { id: 3, section: 'strength', difficulty: 'hard', equipment: 'Dumbbells' },
  { id: 4, section: 'strength', difficulty: 'medium', equipment: 'Resistance band' },
  { id: 5, section: 'chair', difficulty: 'easy', equipment: 'Chair' },
];

test('filterWorkouts with no filters (or "all") returns everything', () => {
  assert.equal(filterWorkouts(FIXTURE_WORKOUTS).length, 5);
  assert.equal(filterWorkouts(FIXTURE_WORKOUTS, { category: 'all' }).length, 5);
});

test('filterWorkouts narrows by category, difficulty, and equipment together', () => {
  const result = filterWorkouts(FIXTURE_WORKOUTS, { category: 'strength', difficulty: 'medium' });
  assert.deepEqual(result.map((w) => w.id), [4]);

  const noneOnly = filterWorkouts(FIXTURE_WORKOUTS, { equipment: 'none' });
  assert.deepEqual(noneOnly.map((w) => w.id).sort(), [1, 2]);
});

test('recentIds only includes history entries inside the lookback window', () => {
  const now = Date.parse('2026-01-10T00:00:00Z');
  const history = [
    { id: 1, shownAt: '2026-01-09T00:00:00Z' }, // 1 day ago
    { id: 2, shownAt: '2026-01-01T00:00:00Z' }, // 9 days ago
  ];
  const ids = recentIds(history, 7, now);
  assert.ok(ids.has(1));
  assert.ok(!ids.has(2));
});

test('pickShuffle avoids anything shown in the last 7 days when possible', () => {
  const now = Date.parse('2026-01-10T00:00:00Z');
  const history = [{ id: 1, shownAt: '2026-01-09T00:00:00Z' }];
  const pool = FIXTURE_WORKOUTS.filter((w) => w.section === 'yoga'); // ids 1, 2

  // Force the "random" pick to always take the first candidate, so the
  // test is deterministic regardless of Math.random.
  const result = pickShuffle(pool, history, { now, random: () => 0 });
  assert.equal(result.workout.id, 2); // id 1 was excluded as recently shown
  assert.equal(result.reused, false);
});

test('pickShuffle falls back to the full pool (and flags reused) once everything has been shown', () => {
  const now = Date.parse('2026-01-10T00:00:00Z');
  const history = [
    { id: 1, shownAt: '2026-01-09T00:00:00Z' },
    { id: 2, shownAt: '2026-01-08T00:00:00Z' },
  ];
  const pool = FIXTURE_WORKOUTS.filter((w) => w.section === 'yoga'); // ids 1, 2, both recent

  const result = pickShuffle(pool, history, { now, random: () => 0 });
  assert.equal(result.reused, true);
  assert.ok([1, 2].includes(result.workout.id));
});

test('pickShuffle returns null for an empty pool', () => {
  assert.equal(pickShuffle([], []), null);
});
