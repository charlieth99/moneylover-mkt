---
name: app-market-research
description: Research a mobile app category in any country from public Google Play data and turn it into an interactive dashboard - top apps ranked by local-language review activity, 6-month trend, feature matrix, what local users praise and complain about (with quotes), and the gaps and 90-day plan for a focal app. Use this whenever someone wants to size up an app market or competitors in a country ("top expense tracker apps in Indonesia", "who leads language-learning apps in Thailand", "market gaps for Money Lover in Vietnam", "analyse reviews of fitness apps in VN", "crawl apps with over 10k downloads a month"), compare app features, mine app-store reviews, or find opportunities for an app before entering a market - even if they don't say "dashboard" or "Google Play".
---

# App market research (Google Play, any country, any category)

This skill reproduces a workflow built with the Money Lover marketing team: they want **numbers they can trust**, said plainly, with the caveats up front, in Vietnamese unless they ask otherwise, and a visual page they can share with their team.

The output is a dashboard (the claude.ai "Data" Artifact type) with these sections, top to bottom:
1. Headline sentence: who leads, their share of local reviews, how many apps are local.
2. Ranking: local-language reviews in the last 30 days, top 20.
3. Trend: 6 monthly windows for the top 8 (small multiples).
4. Feature heatmap: ~25 features × 20 apps (yes / partial / not mentioned).
5. Scatter: number of features vs. local reviews (does feature count buy users?).
6. Reviews: % positive/negative, complaint and praise themes, per-app 1-2★ share, quotes.
7. Gaps: with a focal app, its position vs leaders plus a gap matrix (demand × fit, colored by effort), gap table, 12-week Gantt and risks; without one, the same matrix/table/roadmap framed as "gaps for a new app" (fit = how open the gap is).

## Why the metrics are what they are (tell the user this, briefly)

Google Play does not publish monthly downloads, and the user rejected estimates dressed up as facts. So:
- **Local-language reviews per 30 days** is the main ranking metric. It is a count, not an estimate, and it measures how many people *in that market* are actively using and reviewing the app. Rank order is reliable; absolute level is not downloads.
- **Global installs** (`realInstalls`) are exact but worldwide, never per country. Never present them as local.
- **True downloads** only come from (a) paid panels (Sensor Tower, AppMagic, data.ai, Similarweb App Intelligence) or (b) snapshotting `realInstalls` daily and taking deltas (`scripts/snapshot_installs.py`) — still global, but real. Offer these when the user needs downloads.
- **Gap scores** (demand, fit, effort) are Claude's judgment. Label them as such on the page and name the file "Sample scoring: …".

Read `references/methodology.md` before the first run in a session: it lists the traps found the hard way (Malay reviews counted as Indonesian, the Vietnamese word "ai" matching "AI", apps that only invite happy users to review, newlines in snippets, etc.).

## Workflow

Scripts live in `scripts/` (relative to this file). They need `pip install google-play-scraper` and network access to play.google.com. The App Store is usually blocked in cloud sandboxes; say so if it is.

### 1. Pin down the brief (ask only what you can't infer)
- Country (Play `country` code, e.g. `vn`, `id`, `th`) and the language profile to use.
- Category (e.g. personal finance, language learning, fitness).
- Focal app, if any (package id, e.g. `com.bookmark.money`) — the app whose opportunities the last section assesses.
- Report language (default Vietnamese) and shape: dashboard (KPI-ish) or visual analysis (one finding, top to bottom). If the Artifact view context shows a `form`, build that shape.

### 2. Config
- **Category**: `personal-finance.json` and `english-learning.json` exist. Use one if it fits, else write one following `references/category-config.md` (keywords per language, include/exclude regexes, features with labels and patterns, which features to verify by hand).
- **Language**: `scripts/langs.py` has Indonesian (`id`), Vietnamese (`vi`), Thai (`th`) and English (`en`). For a new market add a profile (marker words that separate it from close neighbours, contrast words like "but", wish words, theme patterns). Test `is_local` on 4-5 sample sentences, including a near-neighbour language, before crawling.

### 3. Crawl (10-25 min; run in the background)
```bash
python scripts/crawl.py --country vn --lang vi --category references/categories/personal-finance.json --out <DIR> --extra-apps com.bookmark.money
```
Writes `apps.json`, `reviews.json`, `crawl_meta.json`. For big markets (US, India) raise `--max-pages` (e.g. 40); apps whose sample still doesn't reach 6 months get `null` for the windows it doesn't cover, and the page draws only covered months. Sanity-check: does the list contain the apps the user or the press would name? If a known leader is missing, add it with `--extra-apps` or widen keywords, and say what was excluded and why (e.g. an investing app that also tracks spending).

### 4. Analyse
```bash
python scripts/analyze.py --dir <DIR> --category <cat.json> --lang vi --top 20
```
First look at the top 20 list: if a full banking/e-wallet super-app got in, rerun with `--exclude-apps <pkg>`. Then read by hand — this is where most of the quality comes from:
- `feature_snippets.txt`: each matched feature with the matched word in `<<…>>`. Correct false hits and mark premium-only or limited ones as `partial` in an `edits.json` (format in `scripts/export_dashboard.py`). Also set short display names, `local_developers` (only those you can verify: name, address, or listing language; leave unknowns out), and `focal_app`.
- `review_samples.txt`: all 1-2★ reviews plus a sample of "but"/wish reviews. From it write 3-5 findings, pick ~16 quotes (complaints, wishes, praise), and gather evidence for each gap. Count evidence with a regex over the critical set rather than guessing.
- Look at `short_review_pct` and `duplicate_text_pct`: a top app with ~0% 1-2★ and >30% duplicates is probably prompting only happy users. Say so as a likely signal, not a fact.

### 5. Export data files
```bash
python scripts/export_dashboard.py --dir <DIR> --category <cat.json> --edits <DIR>/edits.json --out <DIR>/dash
```
Then write `quotes.json` and `gaps.json` yourself (schemas in `references/data-schemas.md`). Quotes in another language than the report get `text_report` (your translation) and `text_local` (original); drop reviewer names.

### 6. Build the dashboard
1. `Artifact` `action: "quickstart"`, `intent: "other"` → create from the Data type with a short title and `auto_open: "after_first_write"`. Read its `design-defaults.md` and `one-writer.md` once.
2. Write a `values.json` (placeholders, the WRITE blocks you authored: findings, verdict, summary, risks; optional exact `replace` pairs for market-specific wording) and run `python scripts/fill_page.py --values values.json --out <DIR>/dash [--no-focal]`, then `node --check <DIR>/dash/page_script.js`. Without a focal app use `--no-focal` and set `GAPS_TITLE` to e.g. "Khoảng trống cho một app mới", `FIT_LABEL` "đối thủ còn bỏ trống", `HAS_LABEL` "Ai đang làm tốt nhất". Keep numbers out of hand-written prose unless they are marked elements.
3. Upload each JSON with `Artifact` publish `asset: true` (one JSON per call), then one `ArtifactData` batch: `dash/meta` (`lang`), `datasets/<id>` for apps, features, sentiment, themes, quotes, gaps (`kind: "file"`, `format: "json"`, `updated`, `fixed: true`), and `files/index.html` with `file_path` = `<DIR>/dash/files_index.json`.
4. Read `data/users/me/check`, `runs`, and `page` (save `page` to a file and grep the text). Fix anything `failed` or any mark that disagrees. Syntax-check the page's script with `node --check` before uploading.

### 7. Hand over (in the user's language)
Lead with the answer: the 3-5 things the data says, with numbers. Then: what's on the page, what is judgment vs. data, the main limitations (Android only, global installs, review ≠ download), that the page is private until they press Share, and the next options (paid panel, daily install deltas, another market). Keep scripts and outputs in the repo if the user wants them kept; commit only if asked or required by the repo's hooks.

## Download trend over 12 months

What exists, in order of trust (say which one a chart uses):
1. **Paid panels** (AppMagic, Sensor Tower, data.ai): per-country monthly downloads with history. Use when the user has an account.
2. **Archived Play pages** (web.archive.org snapshots of `play.google.com/store/apps/details?id=…`): each snapshot carries the exact `realInstalls` of that day, so month-to-month differences are real global downloads, for apps archived often enough. Needs network access to web.archive.org; in cloud sandboxes it is often blocked by the egress proxy — if so, say so and stop, don't route around it.
3. **Daily snapshots from now on** (`scripts/snapshot_installs.py` on a schedule): exact global downloads, but history starts today.
4. **12-month local review trend** (always available): `crawl.py --months 12 --max-pages 40`, then `analyze.py` gives 12 windows per app; set `{{MONTHS}}` to 12. This shows local *usage momentum*, not downloads — label it that way on the page.

## Extending
- New category: add `references/categories/<name>.json`.
- New market language: add a profile to `scripts/langs.py`.
- Category-specific review themes (e.g. "speech recognition is wrong" for language apps): add `themes.<lang>` to the category config; it replaces the language profile's generic themes.
- Real downloads over time: `scripts/snapshot_installs.py` (run daily via a scheduled task; deltas of `realInstalls`).
