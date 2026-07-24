/**
 * workoutLibrary.js
 * ------------------------------------------------------------------
 * The logic behind the "Workout Video Library" feature:
 *   1. Deriving a clean easy/medium/hard difficulty tag from messy
 *      source data (the workout dataset was scraped from a spreadsheet
 *      where the "difficulty" column sometimes contained a workout
 *      *type* instead, e.g. "HIIT" or "Full Body Strength").
 *   2. Filtering the library by category / difficulty / equipment.
 *   3. Shuffling to a pick that hasn't come up in the last N days,
 *      falling back to the full pool (and saying so) once everything
 *      matching the filters has already been used that week.
 *
 * This module is intentionally dataset-agnostic - it operates on plain
 * workout objects of shape { id, section, difficulty, equipment, ... }
 * so it can be unit tested with small fixtures instead of the full
 * 256-video production dataset (see app/75-Challenge-Tracker.html for
 * that).
 */

'use strict';

/**
 * Buckets a messy "difficulty-or-type" string into easy/medium/hard.
 * If the text contains an explicit difficulty word, that wins. If not
 * (e.g. it's really a workout *type* like "Cardio/HIIT"), falls back to
 * inferring difficulty from the reported impact level.
 *
 * @param {string} rawDifficultyOrType
 * @param {string} impact - e.g. "Low", "Moderate", "High", "Moderate–High"
 */
function bucketDifficulty(rawDifficultyOrType, impact) {
  const text = String(rawDifficultyOrType || '').toLowerCase();
  if (text.includes('hard')) return 'hard';
  if (text.includes('medium')) return 'medium';
  if (text.includes('easy')) return 'easy';
  return inferDifficultyFromImpact(impact);
}

function inferDifficultyFromImpact(impact) {
  const text = String(impact || '').toLowerCase();
  if (text.includes('high')) return 'hard';
  if (text.includes('moderate')) return 'medium';
  return 'easy';
}

/** Buckets a free-text equipment description into a short filter tag. */
function equipmentBucket(equipmentText) {
  const text = String(equipmentText || '').toLowerCase();
  if (text.startsWith('none')) return 'none';
  if (text.includes('dumbbell')) return 'dumbbells';
  if (text.includes('band')) return 'band';
  if (text.includes('chair')) return 'chair';
  return 'other';
}

/**
 * @typedef {{ category?: string, difficulty?: string, equipment?: string }} LibraryFilters
 */

/**
 * @param {Array<object>} workouts
 * @param {LibraryFilters} filters - "all" (or omitted) means no constraint
 */
function filterWorkouts(workouts, filters = {}) {
  const { category = 'all', difficulty = 'all', equipment = 'all' } = filters;
  return workouts.filter((w) => {
    if (category !== 'all' && w.section !== category) return false;
    if (difficulty !== 'all' && w.difficulty !== difficulty) return false;
    if (equipment !== 'all' && equipmentBucket(w.equipment) !== equipment) return false;
    return true;
  });
}

/**
 * @param {Array<{id: number|string, shownAt: string}>} history - ISO timestamps
 * @param {number} days
 * @param {number} now - epoch ms, defaults to Date.now()
 * @returns {Set<number|string>} ids shown within the last `days` days
 */
function recentIds(history, days, now = Date.now()) {
  const cutoff = now - days * 24 * 60 * 60 * 1000;
  return new Set(
    history.filter((h) => new Date(h.shownAt).getTime() >= cutoff).map((h) => h.id)
  );
}

/**
 * Picks a workout from `pool`, preferring ones not shown in the last
 * `days` days per `history`. If every matching workout has already been
 * shown in that window, falls back to the full pool and flags `reused`
 * so the caller can tell the user honestly what happened.
 *
 * @param {Array<object>} pool - already-filtered candidate workouts
 * @param {Array<{id: number|string, shownAt: string}>} history
 * @param {object} [options]
 * @param {number} [options.days=7]
 * @param {number} [options.now=Date.now()]
 * @param {() => number} [options.random=Math.random]
 * @returns {{ workout: object, reused: boolean } | null} null if pool is empty
 */
function pickShuffle(pool, history, options = {}) {
  const { days = 7, now = Date.now(), random = Math.random } = options;
  if (pool.length === 0) return null;

  const avoid = recentIds(history, days, now);
  let candidates = pool.filter((w) => !avoid.has(w.id));
  let reused = false;
  if (candidates.length === 0) {
    candidates = pool;
    reused = true;
  }

  const workout = candidates[Math.floor(random() * candidates.length)];
  return { workout, reused };
}

module.exports = {
  bucketDifficulty,
  inferDifficultyFromImpact,
  equipmentBucket,
  filterWorkouts,
  recentIds,
  pickShuffle,
};
