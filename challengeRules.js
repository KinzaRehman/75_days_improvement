/**
 * dateUtils.js
 * ------------------------------------------------------------------
 * Pure date-math helpers for the 75-day challenge window.
 *
 * These mirror the logic embedded inline in app/75-Challenge-Tracker.html
 * (which ships as a single dependency-free file on purpose, so buyers can
 * just double-click and open it). This module exists so the same logic
 * can be unit tested in isolation - see tests/dateUtils.test.js.
 *
 * All functions are pure: no Date.now() / new Date() calls unless a
 * "now" is passed in explicitly (or defaulted as an argument), which
 * keeps everything deterministic and easy to test.
 */

'use strict';

const MS_PER_DAY = 24 * 60 * 60 * 1000;

/**
 * Parses a "YYYY-MM-DD" string (the format <input type="date"> gives you)
 * into a local Date at midnight. Returns null for empty/invalid input.
 * Deliberately avoids `new Date(str)` because that parses as UTC in some
 * engines, which silently shifts the date by a day depending on timezone.
 */
function parseLocalDate(str) {
  if (!str) return null;
  const match = String(str).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;
  const [, y, m, d] = match;
  const date = new Date(Number(y), Number(m) - 1, Number(d));
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Returns a new Date, n days after the given date (n may be negative). */
function addDays(date, n) {
  const result = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  result.setDate(result.getDate() + n);
  return result;
}

/** Formats a Date as "YYYY-MM-DD" (local time, not UTC). */
function toISODate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

/** Strips the time component off a Date, returning midnight local time. */
function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

/**
 * Given a challenge's start date, returns the { start, end } window,
 * where end is inclusive (start + totalDays - 1).
 */
function computeChallengeWindow(startDateStr, totalDays = 75) {
  const start = parseLocalDate(startDateStr);
  if (!start) return null;
  return { start, end: addDays(start, totalDays - 1) };
}

/**
 * How many days remain in the challenge as of `today`.
 * - Before the start date: returns totalDays (challenge hasn't begun).
 * - After the end date: returns 0 (challenge window has passed).
 * - Otherwise: whole days remaining, inclusive of today.
 * Returns null if no valid start date is set.
 */
function daysLeftInChallenge(startDateStr, totalDays = 75, today = new Date()) {
  const window = computeChallengeWindow(startDateStr, totalDays);
  if (!window) return null;
  const t = startOfDay(today);
  if (t < window.start) return totalDays;
  if (t > window.end) return 0;
  return Math.round((window.end - t) / MS_PER_DAY);
}

/**
 * Which challenge day number (1-based) corresponds to `today`, given a
 * start date. Returns null if there's no start date, or if today falls
 * outside the challenge's date range.
 */
function dayNumberForDate(startDateStr, totalDays = 75, today = new Date()) {
  const start = parseLocalDate(startDateStr);
  if (!start) return null;
  const diff = Math.round((startOfDay(today) - start) / MS_PER_DAY) + 1;
  if (diff < 1 || diff > totalDays) return null;
  return diff;
}

module.exports = {
  MS_PER_DAY,
  parseLocalDate,
  addDays,
  toISODate,
  startOfDay,
  computeChallengeWindow,
  daysLeftInChallenge,
  dayNumberForDate,
};
