# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - Portfolio release

### Added
- Extracted core logic (`src/`) - date math, challenge rules, streak
  calculation, CSV export, and workout-library filtering/shuffle -
  pulled out of the client app into small, pure, unit-tested modules.
- Full test suite (`tests/`) using Node's built-in test runner: 39
  tests covering date-window edge cases, all three challenge rule
  sets, streak logic, CSV escaping, and the no-repeat-in-7-days
  shuffle algorithm.
- GitHub Actions CI running the test suite across Node 18/20/22 and a
  smoke test of the analytics script.
- `analytics/` - a real pandas + matplotlib pipeline that reads the
  app's own CSV export format and produces a completion/energy trend
  chart, plus a synthetic sample-data generator.
- `ai/` - a weekly narrative-insight generator with two interchangeable
  modes: a dependency-free rule-based fallback, and a live Claude API
  call, sharing the same prompt-construction and stats pipeline.
- `docs/ARCHITECTURE.md` with a diagram of how the four layers
  (client app, extracted logic, sync backend, analytics/AI) relate.

### Changed
- Workout video library expanded from 134 to 256 videos, recategorized
  into 10 categories (Full Body & HIIT, Strength Training, Pilates &
  Barre, Yoga & Stretching, Boxing & Step, Core & Abs, Chair/Senior/
  Balance, Walking/Cardio/Dance, Household Item Workouts, Prenatal &
  Postnatal).
- Google Sheets backend rebuilt from a single flat "everything" sheet
  into five purpose-built tabs (Start Here, Raw Data, Daily Diary,
  Dashboard, Challenge Rules), with Raw Data as the only writable
  source of truth and every other tab built from formulas.
- Video player switched from an embedded iframe to a thumbnail +
  direct link, after discovering a meaningful share of the source
  videos have third-party embedding disabled by the uploader.
- Theme picker relocated to a dedicated bar at the top of the page.
- Workout library merged into the daily journal panel (previously a
  separate section below the fold), with an explicit "pick from
  library" vs. "I'll do my own workout" toggle.

### Fixed
- `<select>` dropdown option text unreadable in Dark theme (native
  option popups don't inherit page theme variables in most browsers).
- Checklist checkbox-to-label spacing and vertical alignment.
- Journal sidebar growing taller than the Progress Board and leaving a
  large empty gap beneath it on wide viewports - the journal panel now
  caps its own height to the viewport and scrolls internally instead.

## [0.3.0]
- Added Hard/Medium/Soft theme picker (Dark, Light, Pastel), a
  personalization field ("Fill In Name"), and per-challenge start-date
  tracking with an auto-computed end date and days-left countdown.
- Added a unique motivational quote per challenge day (75 originals).

## [0.2.0]
- Added the Google Apps Script sync backend and local JSON
  backup/restore, on top of the original localStorage-only tracker.

## [0.1.0]
- Initial 75 Hard/Medium/Soft tracker: daily checklist, journal fields,
  progress board, and CSV export.
