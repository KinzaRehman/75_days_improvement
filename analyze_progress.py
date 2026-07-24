/**
 * 75 CHALLENGE TRACKER - Google Sheets backend
 * ------------------------------------------------
 * This turns a blank Google Sheet into a 5-tab tracker that stays in sync
 * with the "75 Challenge Tracker" HTML file:
 *
 *   Start Here      - welcome + at-a-glance start dates per challenge
 *   Raw Data        - one row per saved day (hidden - this is the database)
 *   Daily Diary     - pick a challenge + day, see that entry as a readable page
 *   Dashboard       - progress totals per challenge
 *   Challenge Rules - reference table of the Hard / Medium / Soft rules
 *
 * Everything except Raw Data is built from FORMULAS that look up Raw Data by
 * a "Storage Key" (e.g. "75 HARD-day-12"), so the tabs never drift out of
 * sync with each other - there's exactly one place data is written.
 *
 * HOW TO INSTALL (about 5 minutes, one time):
 *  1. Go to https://sheets.google.com and create a new blank spreadsheet.
 *     Name it something like "75 Challenge Tracker".
 *  2. Click Extensions → Apps Script.
 *  3. Delete any placeholder code in the editor, then paste in this ENTIRE
 *     file.
 *  4. Save (Ctrl/Cmd + S).
 *  5. Click Deploy → New deployment → pick type "Web app".
 *     - Execute as: Me.
 *     - Who has access: Anyone.
 *     - Click Deploy and approve the permission prompts (click Advanced →
 *       Go to project (unsafe) → Allow if you see a warning - this is your
 *       own script running under your own account).
 *  6. Copy the Web app URL. It ends in /exec.
 *  7. Paste that URL into the tracker's "Google Apps Script Web App URL"
 *     field, click Save URL, then click "Create/refresh tabs" once.
 *     That builds all five tabs for you.
 *
 * From then on, every "Save day + sync" in the tracker fills in Raw Data,
 * and the other four tabs update themselves automatically.
 *
 * You can also open the Sheet directly and use the "75 Challenge" menu at
 * the top for Daily Diary / Dashboard shortcuts, or to re-run setup.
 */

const APP = Object.freeze({
  MENU: '75 Challenge',
  SHEETS: {
    START: 'Start Here',
    RAW: 'Raw Data',
    DIARY: 'Daily Diary',
    DASHBOARD: 'Dashboard',
    RULES: 'Challenge Rules'
  },
  CHALLENGES: ['75 HARD', '75 MEDIUM', '75 SOFT']
});

// Column order doesn't matter to the formulas below - every lookup finds its
// own column by header name - but keep this list stable once you've saved
// real data, since "Repair / refresh tabs" remaps old rows by header name.
const RAW_HEADERS = Object.freeze([
  'Saved At',
  'Challenge',
  'Day',
  'Day 1 Date',
  'Challenge Date',
  'Overall Complete',
  'Workouts Done',
  'Outdoor Done',
  'Diet Done',
  'Water Done',
  'Reading Done',
  'Photo Done',
  'Workout Rule',
  'Diet Rule',
  'Water Rule',
  'Reading Rule',
  'Photo Rule',
  'Restart Rule',
  'Daily Completion Requires',
  'Water Actual',
  'Pages Read',
  'Mood',
  'Energy',
  'Weight / Measurement',
  'Workout Notes',
  'Meals / Nutrition',
  'Journal',
  'Quote of the Day',
  'Storage Key'
]);

// ─────────────────────────────────────────────────────────────────────────────
// Entry points
// ─────────────────────────────────────────────────────────────────────────────

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu(APP.MENU)
    .addItem('📖 Open Daily Diary', 'openDailyDiary')
    .addItem('📊 Open Dashboard', 'openDashboard')
    .addSeparator()
    .addItem('🗃️ Show Raw Data', 'showRawData')
    .addItem('⚙️ Create / refresh tabs', 'installMasterTemplateFromMenu')
    .addItem('🆘 Help', 'showHelp')
    .addToUi();
}

function doPost(e) {
  try {
    const body = JSON.parse((e && e.postData && e.postData.contents) || '{}');

    if (body.action === 'setup') {
      installMasterTemplate_();
      return respond_({ ok: true, message: 'Tabs created/refreshed.' });
    }

    if (body.action === 'upsertDay') {
      const result = saveDay_(body);
      return respond_(result);
    }

    return respond_({ ok: false, message: 'Unknown action.' });
  } catch (err) {
    return respond_({ ok: false, message: String(err) });
  }
}

function respond_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function installMasterTemplateFromMenu() {
  installMasterTemplate_();
  SpreadsheetApp.getUi().alert(
    APP.MENU,
    'Tabs created/refreshed. Raw Data was preserved and remapped by header name.',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

function installMasterTemplate_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  setupRawData_(getOrCreateSheet_(ss, APP.SHEETS.RAW));
  setupStartHere_(getOrCreateSheet_(ss, APP.SHEETS.START));
  setupRules_(getOrCreateSheet_(ss, APP.SHEETS.RULES));
  setupDailyDiary_(getOrCreateSheet_(ss, APP.SHEETS.DIARY));
  setupDashboard_(getOrCreateSheet_(ss, APP.SHEETS.DASHBOARD));

  const raw = ss.getSheetByName(APP.SHEETS.RAW);
  if (raw && !raw.isSheetHidden()) raw.hideSheet();

  const start = ss.getSheetByName(APP.SHEETS.START);
  if (start) ss.setActiveSheet(start);

  SpreadsheetApp.flush();
  return { ok: true, message: 'Master template installed.' };
}

function openDailyDiary() { activateSheet_(APP.SHEETS.DIARY); }
function openDashboard() { activateSheet_(APP.SHEETS.DASHBOARD); }

function showRawData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(APP.SHEETS.RAW);
  if (!sheet) throw new Error('Raw Data sheet not found. Run "Create / refresh tabs" first.');
  if (sheet.isSheetHidden()) sheet.showSheet();
  ss.setActiveSheet(sheet);
}

function showHelp() {
  SpreadsheetApp.getUi().alert(
    APP.MENU + ' - Help',
    [
      'Data comes from the 75 Challenge Tracker HTML file, not from typing directly into this Sheet.',
      '',
      '1. In the tracker, paste this project\'s Web app URL and click "Create/refresh tabs" once.',
      '2. Every time you click "Save day + sync" in the tracker, that day is written to Raw Data here.',
      '3. Open the Daily Diary tab, choose a Challenge and Day, and the readable journal view fills in automatically.',
      '4. The Dashboard tab totals your progress per challenge.',
      '5. Saving the same challenge + day again updates that row instead of duplicating it.'
    ].join('\n'),
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

function activateSheet_(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error(`Sheet "${sheetName}" not found. Run "Create / refresh tabs" first.`);
  if (sheet.isSheetHidden()) sheet.showSheet();
  ss.setActiveSheet(sheet);
}

// ─────────────────────────────────────────────────────────────────────────────
// Saving a day (called from doPost)
// ─────────────────────────────────────────────────────────────────────────────

function saveDay_(payload) {
  if (!payload || typeof payload !== 'object') throw new Error('No entry data was received.');

  const challenge = normalizeChallenge_(payload.challengeLabel || payload.challengeType);
  const day = Number(payload.day);
  if (!Number.isInteger(day) || day < 1 || day > 75) {
    throw new Error('Challenge day must be a whole number from 1 to 75.');
  }

  const day1Date = parseDateInput_(payload.day1Date);
  const challengeDate = parseDateInput_(payload.challengeDate) || (day1Date ? addDays_(day1Date, day - 1) : null);

  const tasks = payload.tasks || {};
  const actuals = payload.actuals || {};
  const rules = getRulesForChallenge_(challenge);
  const completed = typeof payload.completed === 'boolean' ? payload.completed : calculateCompletion_(challenge, tasks);
  const storageKey = payload.storageKey || `${challenge}-day-${day}`;

  const rowObject = {
    'Saved At': new Date(),
    'Challenge': challenge,
    'Day': day,
    'Day 1 Date': day1Date,
    'Challenge Date': challengeDate,
    'Overall Complete': completed,
    'Workouts Done': Boolean(tasks.workouts),
    'Outdoor Done': Boolean(tasks.outdoor),
    'Diet Done': Boolean(tasks.diet),
    'Water Done': Boolean(tasks.water),
    'Reading Done': Boolean(tasks.reading),
    'Photo Done': Boolean(tasks.photo),
    'Workout Rule': rules.workouts,
    'Diet Rule': rules.diet,
    'Water Rule': rules.water,
    'Reading Rule': rules.reading,
    'Photo Rule': rules.photo,
    'Restart Rule': rules.restart,
    'Daily Completion Requires': rules.required,
    'Water Actual': cleanNumberOrText_(actuals.water),
    'Pages Read': cleanNumberOrText_(actuals.pages),
    'Mood': cleanText_(payload.mood),
    'Energy': cleanNumberOrText_(payload.energy),
    'Weight / Measurement': cleanText_(payload.weight),
    'Workout Notes': cleanText_(payload.workoutNotes),
    'Meals / Nutrition': cleanText_(payload.meals),
    'Journal': cleanText_(payload.journal),
    'Quote of the Day': cleanText_(payload.quote),
    'Storage Key': storageKey
  };

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(APP.SHEETS.RAW);
  if (!sheet) {
    installMasterTemplate_();
    sheet = ss.getSheetByName(APP.SHEETS.RAW);
  }

  const rowValues = RAW_HEADERS.map(header => rowObject[header] ?? '');
  const existingRow = findRowByStorageKey_(sheet, storageKey);

  if (existingRow) {
    sheet.getRange(existingRow, 1, 1, RAW_HEADERS.length).setValues([rowValues]);
  } else {
    sheet.appendRow(rowValues);
  }

  formatRawDataColumns_(sheet);
  SpreadsheetApp.flush();

  return {
    ok: true,
    updated: Boolean(existingRow),
    message: existingRow ? `Updated ${challenge} Day ${day}.` : `Saved ${challenge} Day ${day}.`
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Sheet builders
// ─────────────────────────────────────────────────────────────────────────────

function setupRawData_(sheet) {
  // Preserve existing rows by matching old column names to the current schema,
  // so re-running setup after an update never loses saved entries.
  const existingValues = sheet.getLastRow() > 0 && sheet.getLastColumn() > 0
    ? sheet.getRange(1, 1, sheet.getLastRow(), sheet.getLastColumn()).getValues()
    : [];

  let migratedRows = [];
  if (existingValues.length > 1) {
    const oldHeaders = existingValues[0].map(h => String(h || '').trim());
    migratedRows = existingValues.slice(1)
      .filter(row => row.some(value => value !== '' && value !== null))
      .map(row => {
        const obj = {};
        oldHeaders.forEach((header, i) => { if (header) obj[header] = row[i]; });
        return RAW_HEADERS.map(header => obj[header] ?? '');
      });
  }

  breakApartAll_(sheet);
  sheet.clear();
  sheet.setHiddenGridlines(false);
  sheet.setTabColor('#7A8F80');

  sheet.getRange(1, 1, 1, RAW_HEADERS.length).setValues([RAW_HEADERS]);
  if (migratedRows.length) {
    sheet.getRange(2, 1, migratedRows.length, RAW_HEADERS.length).setValues(migratedRows);
  }

  sheet.getRange(1, 1, 1, RAW_HEADERS.length)
    .setBackground('#20352A').setFontColor('#FFFFFF').setFontWeight('bold')
    .setWrap(true).setVerticalAlignment('middle');
  sheet.setRowHeight(1, 44);
  sheet.setFrozenRows(1);

  if (sheet.getFilter()) sheet.getFilter().remove();
  sheet.getRange(1, 1, Math.max(2, sheet.getLastRow()), RAW_HEADERS.length).createFilter();

  for (let col = 1; col <= RAW_HEADERS.length; col++) sheet.setColumnWidth(col, 130);
  ['Workout Notes', 'Meals / Nutrition', 'Journal', 'Quote of the Day'].forEach(h => {
    sheet.setColumnWidth(RAW_HEADERS.indexOf(h) + 1, 230);
  });

  formatRawDataColumns_(sheet);
}

function setupStartHere_(sheet) {
  breakApartAll_(sheet);
  sheet.clear();
  sheet.setHiddenGridlines(true);
  sheet.setTabColor('#C69749');

  [190, 360, 30, 220, 220].forEach((w, i) => sheet.setColumnWidth(i + 1, w));

  sheet.getRange('A1:E2').merge()
    .setValue('🌿 75 DAY CHALLENGE TRACKER')
    .setBackground('#20352A').setFontColor('#FFFFFF').setFontSize(22).setFontWeight('bold')
    .setHorizontalAlignment('center').setVerticalAlignment('middle');
  sheet.setRowHeights(1, 2, 34);

  sheet.getRange('A4:E4').merge()
    .setValue('Welcome to your private challenge journal')
    .setFontSize(14).setFontColor('#44624A').setFontWeight('bold').setHorizontalAlignment('center');

  sheet.getRange('A6:B10').setValues([
    ['STEP', 'WHAT TO DO'],
    ['1', 'Open the 75-Challenge-Tracker.html file and set a start date, pick Hard/Medium/Soft.'],
    ['2', 'Paste this Sheet\'s web app URL into the tracker and click "Create/refresh tabs" once.'],
    ['3', 'Check off each day in the tracker and click "Save day + sync".'],
    ['4', 'Come back here any time - Daily Diary and Dashboard update on their own.']
  ]);
  sheet.getRange('A6:B6').setBackground('#44624A').setFontColor('#FFFFFF').setFontWeight('bold');
  sheet.getRange('A6:B10').setWrap(true).setVerticalAlignment('middle')
    .setBorder(true, true, true, true, true, true, '#E2D8CB', SpreadsheetApp.BorderStyle.SOLID);

  sheet.getRange('D6:E6').merge()
    .setValue('YOUR START DATES')
    .setBackground('#C69749').setFontColor('#FFFFFF').setFontWeight('bold').setHorizontalAlignment('center');
  sheet.getRange('D7:E7').merge().setValue('Challenge').setFontWeight('bold').setBackground('#FBF1DC');
  APP.CHALLENGES.forEach((challenge, i) => {
    const row = 8 + i;
    sheet.getRange(row, 4).setValue(challenge).setBackground('#FAF8F5').setFontWeight('bold');
    sheet.getRange(row, 5).setFormula(startDateLookupFormula_(challenge)).setNumberFormat('mmm d, yyyy').setBackground('#FAF8F5');
  });
  sheet.getRange('D7:E10').setBorder(true, true, true, true, true, true, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);

  sheet.getRange('A18:E19').merge()
    .setValue('Privacy note: entries save inside this spreadsheet copy. Do not share edit access if your journal contains private information.')
    .setBackground('#F5F0EB').setFontColor('#6B625B').setWrap(true).setVerticalAlignment('middle');
}

function setupRules_(sheet) {
  breakApartAll_(sheet);
  sheet.clear();
  sheet.setHiddenGridlines(true);
  sheet.setTabColor('#6B8E72');

  const rules = [
    ['Challenge', 'Workouts', 'Diet', 'Water', 'Reading', 'Progress Photos', 'Restart Rule', 'Daily Completion Requires'],
    ['75 HARD', '2x/day, one outside', 'Strict, no cheats', '1 gallon/day', '10 pages, no audiobooks', 'Daily', 'Must restart at mistake', 'Workouts, Outdoor, Diet, Water, Reading, Photo'],
    ['75 MEDIUM', '1x/day, anywhere', 'Healthy, 1 treat/week', '80–100 oz/day', '10 pages or audiobooks', '3–4x/week', 'Restart only if quitting', 'Workouts, Diet, Water, Reading'],
    ['75 SOFT', '1x/day, any activity', 'Healthy, flexible', '~64 oz/day', '10 pages, any book', 'Optional', 'No restart needed', 'Workouts, Diet, Water, Reading']
  ];

  sheet.getRange(1, 1, rules.length, rules[0].length).setValues(rules);
  sheet.getRange('A1:H1').setBackground('#20352A').setFontColor('#FFFFFF').setFontWeight('bold');
  sheet.getRange('A1:H4').setWrap(true).setVerticalAlignment('middle')
    .setBorder(true, true, true, true, true, true, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);
  sheet.setFrozenRows(1);
  [120, 190, 190, 145, 190, 150, 190, 280].forEach((w, i) => sheet.setColumnWidth(i + 1, w));
  sheet.setRowHeights(2, 3, 52);
}

function setupDailyDiary_(sheet) {
  breakApartAll_(sheet);
  sheet.clear();
  sheet.setHiddenGridlines(true);
  sheet.setTabColor('#C69749');

  Array(8).fill(135).forEach((w, i) => sheet.setColumnWidth(i + 1, w));

  sheet.getRange('A1:H2').merge()
    .setValue('📖 MY 75 DAY JOURNAL')
    .setBackground('#20352A').setFontColor('#FFFFFF').setFontWeight('bold').setFontSize(22)
    .setHorizontalAlignment('center').setVerticalAlignment('middle');
  sheet.setRowHeights(1, 2, 34);

  sheet.getRange('A4').setValue('Challenge').setFontWeight('bold').setFontColor('#44624A');
  sheet.getRange('B4:C4').merge().setValue('75 HARD');
  sheet.getRange('E4').setValue('Challenge Day').setFontWeight('bold').setFontColor('#44624A');
  sheet.getRange('F4:G4').merge().setValue(1);

  sheet.getRange('B4:C4').setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(APP.CHALLENGES, true).setAllowInvalid(false).build()
  );
  sheet.getRange('F4:G4').setDataValidation(
    SpreadsheetApp.newDataValidation().requireNumberBetween(1, 75).setAllowInvalid(false).build()
  );
  sheet.getRange('B4:C4').setBackground('#FBF1DC').setFontWeight('bold').setHorizontalAlignment('center');
  sheet.getRange('F4:G4').setBackground('#FBF1DC').setFontWeight('bold').setHorizontalAlignment('center');

  sheet.getRange('A5:H5').merge()
    .setValue('Choose a challenge and day above. Everything below updates automatically from Raw Data.')
    .setFontColor('#7A7A7A').setFontStyle('italic').setHorizontalAlignment('center');

  sectionHeader_(sheet, 'A7:H7', 'ENTRY OVERVIEW');
  label_(sheet, 'A8', 'Challenge Date');
  sheet.getRange('B8:C8').merge().setFormula(lookupFormula_('Challenge Date')).setNumberFormat('mmm d, yyyy');
  label_(sheet, 'D8', 'Saved At');
  sheet.getRange('E8:H8').merge().setFormula(lookupFormula_('Saved At')).setNumberFormat('mmm d, yyyy h:mm AM/PM');

  label_(sheet, 'A9', 'Day 1 Date');
  sheet.getRange('B9:C9').merge().setFormula(lookupFormula_('Day 1 Date')).setNumberFormat('mmm d, yyyy');
  label_(sheet, 'D9', 'Mood');
  sheet.getRange('E9:F9').merge().setFormula(lookupFormula_('Mood'));
  label_(sheet, 'G9', 'Energy');
  sheet.getRange('H9').setFormula(lookupFormula_('Energy'));

  label_(sheet, 'A10', 'Weight / Measurement');
  sheet.getRange('B10:D10').merge().setFormula(lookupFormula_('Weight / Measurement'));
  label_(sheet, 'E10', 'Pages Read');
  sheet.getRange('F10').setFormula(lookupFormula_('Pages Read'));
  label_(sheet, 'G10', 'Water Actual');
  sheet.getRange('H10').setFormula(lookupFormula_('Water Actual'));

  sectionHeader_(sheet, 'A12:H12', 'COMPLETION SNAPSHOT');
  statusPair_(sheet, 13, 'Overall Complete', 'Overall Complete', 'Workout(s)', 'Workouts Done');
  statusPair_(sheet, 14, 'Outdoor', 'Outdoor Done', 'Diet', 'Diet Done');
  statusPair_(sheet, 15, 'Water', 'Water Done', 'Reading', 'Reading Done');
  statusPair_(sheet, 16, 'Photo', 'Photo Done', 'Daily Requirement', 'Daily Completion Requires', true);

  sectionHeader_(sheet, 'A18:H18', 'QUOTE FOR THIS DAY');
  sheet.getRange('A19:H20').merge()
    .setFormula(lookupFormula_('Quote of the Day'))
    .setBackground('#FBF1DC').setFontColor('#44624A').setFontStyle('italic').setFontWeight('bold')
    .setWrap(true).setHorizontalAlignment('center').setVerticalAlignment('middle');

  sectionHeader_(sheet, 'A22:H22', 'DAILY REFLECTION');
  sheet.getRange('A23:H28').merge()
    .setFormula(lookupFormula_('Journal'))
    .setBackground('#FAF8F5').setWrap(true).setVerticalAlignment('top')
    .setBorder(true, true, true, true, false, false, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);
  sheet.setRowHeights(23, 6, 28);

  sectionHeader_(sheet, 'A30:D30', 'MEALS / NUTRITION');
  sectionHeader_(sheet, 'E30:H30', 'WORKOUT NOTES');
  sheet.getRange('A31:D36').merge()
    .setFormula(lookupFormula_('Meals / Nutrition'))
    .setBackground('#FAF8F5').setWrap(true).setVerticalAlignment('top')
    .setBorder(true, true, true, true, false, false, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);
  sheet.getRange('E31:H36').merge()
    .setFormula(lookupFormula_('Workout Notes'))
    .setBackground('#FAF8F5').setWrap(true).setVerticalAlignment('top')
    .setBorder(true, true, true, true, false, false, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);
  sheet.setRowHeights(31, 6, 28);

  sheet.getRange('A38:H38').merge()
    .setValue('🌿 One day at a time. This page is built from the entries saved through the tracker.')
    .setBackground('#F5F0EB').setFontColor('#6B625B').setHorizontalAlignment('center').setFontStyle('italic');

  sheet.getRange('A7:H38').setFontFamily('Arial').setFontSize(10);
  sheet.setFrozenRows(5);
}

function setupDashboard_(sheet) {
  breakApartAll_(sheet);
  sheet.clear();
  sheet.setHiddenGridlines(true);
  sheet.setTabColor('#44624A');

  [180, 150, 130, 150, 140, 190].forEach((w, i) => sheet.setColumnWidth(i + 1, w));

  sheet.getRange('A1:F2').merge()
    .setValue('📊 75 CHALLENGE DASHBOARD')
    .setBackground('#20352A').setFontColor('#FFFFFF').setFontWeight('bold').setFontSize(22)
    .setHorizontalAlignment('center').setVerticalAlignment('middle');
  sheet.setRowHeights(1, 2, 34);

  sheet.getRange('A4:F4').setValues([[
    'Challenge', 'Completed Days', 'Progress %', 'Diary Entries', 'Avg Energy', 'Last Saved'
  ]]);
  sheet.getRange('A4:F4').setBackground('#44624A').setFontColor('#FFFFFF').setFontWeight('bold');
  sheet.getRange('A5:A7').setValues(APP.CHALLENGES.map(x => [x]));

  const challengeCol = col_('Challenge');
  const completeCol = col_('Overall Complete');
  const journalCol = col_('Journal');
  const energyCol = col_('Energy');
  const savedAtCol = col_('Saved At');

  for (let row = 5; row <= 7; row++) {
    sheet.getRange(row, 2).setFormula(`=COUNTIFS('Raw Data'!$${challengeCol}:$${challengeCol},$A${row},'Raw Data'!$${completeCol}:$${completeCol},TRUE)`);
    sheet.getRange(row, 3).setFormula(`=B${row}/75`).setNumberFormat('0%');
    sheet.getRange(row, 4).setFormula(`=COUNTIFS('Raw Data'!$${challengeCol}:$${challengeCol},$A${row},'Raw Data'!$${journalCol}:$${journalCol},"<>")`);
    sheet.getRange(row, 5).setFormula(`=IFERROR(AVERAGEIF('Raw Data'!$${challengeCol}:$${challengeCol},$A${row},'Raw Data'!$${energyCol}:$${energyCol}),"")`).setNumberFormat('0.0');
    sheet.getRange(row, 6).setFormula(`=IFERROR(MAX(FILTER('Raw Data'!$${savedAtCol}:$${savedAtCol},'Raw Data'!$${challengeCol}:$${challengeCol}=$A${row})),"")`).setNumberFormat('mmm d, yyyy h:mm AM/PM');
  }
  sheet.getRange('A4:F7').setBorder(true, true, true, true, true, true, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);

  sectionHeader_(sheet, 'A10:F10', 'HOW TO USE YOUR PROGRESS VIEW');
  sheet.getRange('A11:F14').merge()
    .setValue('Completed Days counts entries that satisfy the daily completion rules for that challenge. Diary Entries counts saved daily reflections. Open the Daily Diary tab to select a challenge and day and read the full journal entry, including that day\'s quote.')
    .setBackground('#FAF8F5').setWrap(true).setVerticalAlignment('top')
    .setBorder(true, true, true, true, false, false, '#D4C5B0', SpreadsheetApp.BorderStyle.SOLID);
  sheet.setRowHeights(11, 4, 28);
}

// ─────────────────────────────────────────────────────────────────────────────
// Formula helpers
// ─────────────────────────────────────────────────────────────────────────────

function breakApartAll_(sheet) {
  const rows = Math.max(1, sheet.getMaxRows());
  const cols = Math.max(1, sheet.getMaxColumns());
  sheet.getRange(1, 1, rows, cols).breakApart();
}

function sectionHeader_(sheet, a1, title) {
  sheet.getRange(a1).merge()
    .setValue(title)
    .setBackground('#44624A').setFontColor('#FFFFFF').setFontWeight('bold')
    .setHorizontalAlignment('left').setVerticalAlignment('middle');
}

function label_(sheet, a1, text) {
  const range = sheet.getRange(a1);
  if (range.getNumColumns() > 1 || range.getNumRows() > 1) range.merge();
  range.setValue(text)
    .setFontWeight('bold').setFontColor('#44624A').setBackground('#F5F0EB')
    .setWrap(true).setVerticalAlignment('middle');
}

function statusPair_(sheet, row, leftLabel, leftField, rightLabel, rightField, rightIsText) {
  label_(sheet, `A${row}:B${row}`, leftLabel);
  sheet.getRange(`C${row}:D${row}`).merge()
    .setFormula(statusFormula_(leftField))
    .setBackground('#FAF8F5').setHorizontalAlignment('center');

  label_(sheet, `E${row}:F${row}`, rightLabel);
  sheet.getRange(`G${row}:H${row}`).merge()
    .setFormula(rightIsText ? lookupFormula_(rightField) : statusFormula_(rightField))
    .setBackground('#FAF8F5').setWrap(true)
    .setHorizontalAlignment(rightIsText ? 'left' : 'center');
}

function lookupFormula_(fieldName) {
  const fieldCol = col_(fieldName);
  const keyCol = col_('Storage Key');
  return `=IFERROR(INDEX('Raw Data'!$${fieldCol}$2:$${fieldCol},MATCH($B$4&"-day-"&$F$4,'Raw Data'!$${keyCol}$2:$${keyCol},0)),"")`;
}

function statusFormula_(fieldName) {
  const fieldCol = col_(fieldName);
  const keyCol = col_('Storage Key');
  return `=IFERROR(IF(INDEX('Raw Data'!$${fieldCol}$2:$${fieldCol},MATCH($B$4&"-day-"&$F$4,'Raw Data'!$${keyCol}$2:$${keyCol},0)),"✅ Complete","⬜ Not complete"),"")`;
}

function startDateLookupFormula_(challenge) {
  const dayCol = col_('Day 1 Date');
  const challengeCol = col_('Challenge');
  return `=IFERROR(MAX(FILTER('Raw Data'!$${dayCol}:$${dayCol},'Raw Data'!$${challengeCol}:$${challengeCol}="${challenge}")),"")`;
}

function col_(headerName) {
  const index = RAW_HEADERS.indexOf(headerName);
  if (index === -1) throw new Error(`Unknown Raw Data column: ${headerName}`);
  return columnLetter_(index + 1);
}

function columnLetter_(columnNumber) {
  let temp = '';
  let n = columnNumber;
  while (n > 0) {
    const mod = (n - 1) % 26;
    temp = String.fromCharCode(65 + mod) + temp;
    n = Math.floor((n - mod) / 26);
  }
  return temp;
}

function formatRawDataColumns_(sheet) {
  const maxRows = Math.max(2, sheet.getMaxRows());
  sheet.getRange(2, 1, maxRows - 1, 1).setNumberFormat('mmm d, yyyy h:mm AM/PM');
  sheet.getRange(2, col_('Day 1 Date'), maxRows - 1, 1).setNumberFormat('mmm d, yyyy');
  sheet.getRange(2, col_('Challenge Date'), maxRows - 1, 1).setNumberFormat('mmm d, yyyy');
  sheet.getRange(2, 1, maxRows - 1, RAW_HEADERS.length).setVerticalAlignment('top').setWrap(true);
}

function findRowByStorageKey_(sheet, storageKey) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return null;
  const keyCol = RAW_HEADERS.indexOf('Storage Key') + 1;
  const values = sheet.getRange(2, keyCol, lastRow - 1, 1).getDisplayValues().flat();
  const index = values.findIndex(value => value === storageKey);
  return index === -1 ? null : index + 2;
}

function getOrCreateSheet_(ss, name) {
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

// ─────────────────────────────────────────────────────────────────────────────
// Small utilities
// ─────────────────────────────────────────────────────────────────────────────

function normalizeChallenge_(challenge) {
  const value = String(challenge || '').trim().toUpperCase();
  if (!APP.CHALLENGES.includes(value)) throw new Error('Choose 75 HARD, 75 MEDIUM, or 75 SOFT.');
  return value;
}

function calculateCompletion_(challenge, tasks) {
  const base = Boolean(tasks.workouts && tasks.diet && tasks.water && tasks.reading);
  if (challenge === '75 HARD') return base && Boolean(tasks.outdoor && tasks.photo);
  return base;
}

function getRulesForChallenge_(challenge) {
  const rules = {
    '75 HARD': { water: '1 gallon/day', reading: '10 pages, no audiobooks', workouts: '2x/day, one outside', diet: 'Strict diet, no cheats', photo: 'Daily', restart: 'Must restart at mistake', required: 'Workouts, Outdoor, Diet, Water, Reading, Photo' },
    '75 MEDIUM': { water: '80–100 oz/day', reading: '10 pages or audiobooks', workouts: '1x/day, anywhere', diet: 'Healthy, 1 treat/week', photo: '3–4x/week', restart: 'Restart only if quitting', required: 'Workouts, Diet, Water, Reading' },
    '75 SOFT': { water: '~64 oz/day', reading: '10 pages, any book', workouts: '1x/day, any activity', diet: 'Healthy, flexible', photo: 'Optional', restart: 'No restart needed', required: 'Workouts, Diet, Water, Reading' }
  };
  return rules[challenge];
}

function parseDateInput_(value) {
  if (!value) return null;
  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value)) {
    return new Date(value.getFullYear(), value.getMonth(), value.getDate());
  }
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  return isNaN(date) ? null : date;
}

function addDays_(date, amount) {
  const result = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  result.setDate(result.getDate() + amount);
  return result;
}

function cleanText_(value) { return value == null ? '' : String(value).trim(); }

function cleanNumberOrText_(value) {
  if (value === '' || value == null) return '';
  const number = Number(value);
  return Number.isFinite(number) ? number : String(value).trim();
}
