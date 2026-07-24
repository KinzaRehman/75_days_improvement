/**
 * streak.js
 * ------------------------------------------------------------------
 * Computes the "current streak" shown on the Progress Board: the number
 * of consecutive completed days trailing the end of the array. Any
 * incomplete day resets the count, so the loop naturally lands on the
 * length of the most recent unbroken run.
 */

'use strict';

/**
 * @param {Array<{completed: boolean}>} days - ordered day 1..N records
 * @returns {number} current streak length
 */
function calcStreak(days) {
  let streak = 0;
  for (const day of days) {
    streak = day && day.completed ? streak + 1 : 0;
  }
  return streak;
}

module.exports = { calcStreak };
