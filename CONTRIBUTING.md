# Contributing

This started as a personal project, so the workflow stays pretty
lightweight. If you're picking it up for the first time:

## Getting set up

```bash
git clone https://github.com/KinzaRehman/75_days_improvement.git
cd 75_days_improvement
node --test tests/          # run the JS unit tests (no npm install needed)
pip install -r analytics/requirements.txt
python analytics/analyze_progress.py --input analytics/sample_data/sample_export.csv --output analytics/out
```

No build step for the client app - `app/75-Challenge-Tracker.html` is a
single dependency-free file. Open it directly in a browser to work on
the UI.

## Where things live

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full layout.
Short version: `app/` is the shippable product, `src/` is the same
core logic pulled out into tested modules, `backend/` is the Google
Apps Script sync layer, and `analytics/` + `ai/` are the data pipeline.

## Making a change

1. If you're changing logic that exists in both `app/*.html` and
   `src/*.js` (date math, challenge rules, the shuffle algorithm),
   update both and make sure `node --test tests/` still passes. Keeping
   these in sync manually is a known tradeoff of shipping the app as a
   single dependency-free file - see `docs/ARCHITECTURE.md` for why.
2. Add or update a test alongside any logic change in `src/`.
3. Run `npm run lint` and `npm run format` before committing (requires
   `npm install` once, since ESLint/Prettier are dev dependencies).
4. Keep commit messages descriptive - this repo doesn't enforce a
   specific convention, but "what changed and why" beats "fix stuff."

## Reporting a bug

Open an issue with: what you expected, what happened instead, and
(if relevant) which theme/challenge/browser you were using - a lot of
this app's surface area is CSS across three themes, so that detail
matters more than usual.
