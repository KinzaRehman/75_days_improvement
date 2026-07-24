/**
 * challengeRules.js
 * ------------------------------------------------------------------
 * The Hard / Medium / Soft rule sets, and the pure function that decides
 * whether a given day's checked-off tasks satisfy that challenge's rules.
 */

'use strict';

const RULES = Object.freeze({
  hard: {
    label: '75 HARD',
    workouts: '2 workouts/day, one outside',
    diet: 'Strict diet, no cheats',
    water: '1 gallon/day',
    reading: '10 pages, no audiobooks',
    photo: 'Daily progress photo',
    restart: 'Must restart at mistake',
    required: ['workouts', 'outdoor', 'diet', 'water', 'reading', 'photo'],
  },
  medium: {
    label: '75 MEDIUM',
    workouts: '1 workout/day, anywhere',
    diet: 'Healthy eating, 1 treat/week',
    water: '80\u2013100 oz/day',
    reading: '10 pages or audiobook',
    photo: 'Progress photo 3\u20134x/week',
    restart: 'Restart only if quitting',
    required: ['workouts', 'diet', 'water', 'reading'],
  },
  soft: {
    label: '75 SOFT',
    workouts: '1 activity/day',
    diet: 'Healthy, flexible',
    water: '~64 oz/day',
    reading: '10 pages, any book',
    photo: 'Optional',
    restart: 'No restart needed',
    required: ['workouts', 'diet', 'water', 'reading'],
  },
});

/**
 * A day is complete when every task in that challenge's `required` list
 * is checked. Optional tasks (e.g. photo, for Medium/Soft) don't count.
 *
 * @param {'hard'|'medium'|'soft'} challengeKey
 * @param {Record<string, boolean>} tasks
 */
function isDayComplete(challengeKey, tasks = {}) {
  const rule = RULES[challengeKey];
  if (!rule) throw new Error(`Unknown challenge: ${challengeKey}`);
  return rule.required.every((key) => Boolean(tasks[key]));
}

module.exports = { RULES, isDayComplete };
