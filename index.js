/**
 * csvExport.js
 * ------------------------------------------------------------------
 * Small, dependency-free CSV helpers. Mirrors the export logic in
 * app/75-Challenge-Tracker.html's "Export CSV" button, pulled out here
 * so the quoting/escaping edge cases can be unit tested directly.
 */

'use strict';

/** Wraps a single value in quotes and doubles any embedded quote chars. */
function escapeCsvValue(value) {
  const str = value === null || value === undefined ? '' : String(value);
  return `"${str.replace(/"/g, '""')}"`;
}

/** Turns one array of raw values into a single quoted, comma-joined CSV row. */
function toCsvRow(values) {
  return values.map(escapeCsvValue).join(',');
}

/**
 * Builds a full CSV string (header + data rows), joined with \n.
 * @param {string[]} header
 * @param {Array<Array<any>>} rows
 */
function rowsToCsv(header, rows) {
  const lines = [toCsvRow(header), ...rows.map(toCsvRow)];
  return lines.join('\n');
}

module.exports = { escapeCsvValue, toCsvRow, rowsToCsv };
