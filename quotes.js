'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { escapeCsvValue, toCsvRow, rowsToCsv } = require('../src/csvExport');

test('escapeCsvValue always quotes, even plain values', () => {
  assert.equal(escapeCsvValue('hello'), '"hello"');
  assert.equal(escapeCsvValue(42), '"42"');
});

test('escapeCsvValue doubles embedded quote characters', () => {
  assert.equal(escapeCsvValue('She said "go"'), '"She said ""go"""');
});

test('escapeCsvValue treats null/undefined as an empty string', () => {
  assert.equal(escapeCsvValue(null), '""');
  assert.equal(escapeCsvValue(undefined), '""');
});

test('toCsvRow joins escaped values with commas', () => {
  assert.equal(toCsvRow(['a', 1, true]), '"a","1","true"');
});

test('rowsToCsv builds a header row plus one line per data row', () => {
  const csv = rowsToCsv(
    ['Day', 'Completed'],
    [
      [1, true],
      [2, false],
    ]
  );
  assert.equal(csv, '"Day","Completed"\n"1","true"\n"2","false"');
});

test('a value containing a comma stays inside its own quoted field', () => {
  const csv = rowsToCsv(['Notes'], [['ran, then stretched']]);
  assert.equal(csv, '"Notes"\n"ran, then stretched"');
});
