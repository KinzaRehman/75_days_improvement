# 75 Day Challenge Tracker

[![CI](https://github.com/KinzaRehman/75_days_improvement/actions/workflows/ci.yml/badge.svg)](https://github.com/KinzaRehman/75_days_improvement/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](package.json)

A themeable, offline-first habit tracker for the 75 Hard / Medium / Soft
challenges. It's got a 256-video workout library that avoids repeating
a pick within 7 days, an optional Google Sheets sync backend, and a
small Python analytics + AI pipeline that turns your exported progress
into charts and plain-language weekly recaps.

I originally built this as a real product to sell. This repo is a
restructured version of it that also shows the engineering underneath:
extracted and tested logic, CI, and a working data pipeline built on
top of the app's own CSV export.

> **Quick note on the two licenses here:** the code in this repo is
> MIT-licensed. The compiled single-file app is also sold separately as
> a personal-use digital product (see the footer note inside
> [`app/75-Challenge-Tracker.html`](app/75-Challenge-Tracker.html)). If
> you're a hiring manager reading this, the short version is: the code
> is open, per [`LICENSE`](LICENSE).

## What's in it

- **Hard / Medium / Soft challenge modes**, each with its own rules,
  daily checklist, and its own 75-day progress board.
- **Dark / Light / Pastel themes**, plus a name field that retitles the
  whole app ("Jordan's 75 Challenge Tracker").
- **A start-date-driven countdown.** Set a start date once and the end
  date, days-left counter, and "jump to today" all take care of
  themselves.
- **75 original daily quotes** I wrote for this project (see
  [`src/quotes.js`](src/quotes.js) for why I didn't just scrape a quote
  list from somewhere).
- **A 256-video workout library** across 10 categories, filterable by
  category, difficulty, and equipment. The shuffle avoids repeating
  anything you've already been shown in the last 7 days, and tells you
  honestly when you've run through everything a narrow filter has to
  offer.
- **Optional Google Sheets sync.** A Google Apps Script web app writes
  to one "Raw Data" sheet. Four other tabs (Start Here, Daily Diary,
  Dashboard, Challenge Rules) are read-only views built entirely from
  spreadsheet formulas, so there's no way for them to drift out of sync
  with the real data.
- **Local backup/restore and CSV export**, since everything otherwise
  just lives in `localStorage`.
- **An analytics + AI layer** that runs on top of that CSV export, more
  on that below.

## Tech stack

| Layer | Tech |
|---|---|
| Client app | Vanilla HTML/CSS/JS, no build step, no dependencies |
| Core logic | Node.js (CommonJS), tested with the built-in `node:test` runner |
| Sync backend | Google Apps Script (V8 runtime), Google Sheets as the data store |
| Analytics | Python, pandas, matplotlib |
| AI insights | Python, Anthropic API (Claude), with a dependency-free mock mode |
| CI | GitHub Actions, Node 18/20/22 matrix plus a Python smoke test |

## Repo layout

```
app/          The actual product - a single dependency-free HTML file
backend/      Google Apps Script sync backend, plus its own README
src/          Core logic pulled out into small, tested modules
tests/        Node's built-in test runner, 39 tests, no test-framework dependency
analytics/    pandas/matplotlib pipeline over the CSV export, plus sample data
ai/           Weekly insight generator (rule-based mock or a live Claude call)
docs/         Architecture notes and a diagram
.github/      CI workflow
```

## Getting started

### Run the app
Open `app/75-Challenge-Tracker.html` in a browser. That's it, no install.

### Run the tests
```bash
node --test tests/
```
No `npm install` needed here. The suite uses Node's built-in
`node:test` and `node:assert`, so it works right after you clone.

### Run the analytics pipeline
```bash
pip install -r analytics/requirements.txt
python analytics/analyze_progress.py \
  --input analytics/sample_data/sample_export.csv \
  --output analytics/out
```
Prints a completion rate / streak / mood / energy summary and writes
`analytics/out/progress_chart.png`. There's a sample chart already
sitting in [`docs/images/`](docs/images) if you'd rather look before
running anything.

### Run the AI weekly insight generator
```bash
# No API key needed, this is the rule-based fallback:
python ai/generate_weekly_insight.py --input analytics/sample_data/sample_export.csv

# With a real Claude call instead:
export ANTHROPIC_API_KEY=sk-...
pip install -r ai/requirements.txt
python ai/generate_weekly_insight.py --input analytics/sample_data/sample_export.csv --mode live
```

## Google Sheets sync setup

1. Create a blank Google Sheet.
2. Open **Extensions → Apps Script**, clear out the placeholder code,
   and paste in everything from `backend/AppsScript-Backend.gs`.
3. **Deploy → New deployment → Web app.** Execute as **Me**, access set
   to **Anyone**, then deploy and click through the permission prompts.
4. Copy the `/exec` URL, paste it into the tracker's Script URL field,
   click **Save URL**, then **Create/refresh tabs**.

More detail on what each of the five tabs actually does lives in
[`backend/README.md`](backend/README.md).

## Why there's a src/ *and* an app/

The client app ships as one HTML file on purpose. It's meant for
non-technical buyers who just want to double-click it and go, so there's
no build step and no bundler. The tradeoff is that its inline
`<script>` isn't something a test runner can import directly.

So the parts of the logic that actually benefit from tests, the date
math, the challenge completion rules, the streak calculation, CSV
escaping, and the 7-day no-repeat shuffle, are pulled out into `src/` as
plain functions and tested there. More on the reasoning (and what this
tradeoff costs you) in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```bash
$ node --test tests/
▶ tests (39 total)
  ✔ 39 passed, 0 failed
```

## Things I'd add with more time

- Move `src/` to TypeScript so the workout dataset shape is checked at
  compile time instead of just at test time.
- Swap the Apps Script backend for a small hosted API (Cloudflare
  Workers + D1, probably) as an alternative to Google Sheets.
- Playwright tests against the actual HTML app, not just the extracted logic.
- Have the AI layer flag early signs of burnout or overtraining from
  the mood/energy/impact data it's already collecting.

## License

Code in this repo is [MIT licensed](LICENSE).
