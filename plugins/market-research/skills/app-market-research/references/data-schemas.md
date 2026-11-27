# Dashboard datasets

Ids must match exactly; the page template reads these columns.

## apps (export_dashboard.py)
`rank, app, play_title, developer, package, built_locally ("Yes"/"No"), local_reviews_30d, global_installs, rating, ads ("Yes"/"No"), price_range, last_updated, is_focal ("Yes"/"No"), reviews_to_<YYYY-MM-DD>` (one per 30-day window, oldest first) `, <feature name>` ("yes"/"partial"/"no", one column per feature in the category config).

## features (export_dashboard.py)
`feature` (column name in apps), `label` (display label).

## sentiment (export_dashboard.py)
`app, package, reviews_period, positive, neutral, negative, avg_stars, positive_pct, negative_pct, dev_reply_to_negative_pct (null if no negatives), short_review_pct, duplicate_text_pct, top_complaint`.

## themes (export_dashboard.py)
`theme, kind ("complaint"/"praise"), critical_reviews, negative_reviews, positive_reviews`.

## quotes (you write)
```json
{"id": "q1", "app": "Sổ Thu Chi MISA", "stars": 1, "date": "2026-09-11", "kind": "neg|wish|pos",
 "theme": "Giá / bắt trả premium", "text_local": "original text", "text_report": "translation or same text"}
```
12-16 quotes: ~8 complaints across apps and themes, ~4 wishes, ~3 praise. Exact text from reviews.json (truncate ~300 chars), no names.

## gaps (you write; only with a focal app)
```json
{"id": "g1", "gap": "full name", "short": "≤22 chars", "demand": 1-3, "fit": 1-3, "effort": 1-3,
 "review_mentions": 46 or null, "evidence": "…", "competitors": "…", "focal_has": "…", "action": "…",
 "week_start": 1-12, "week_end": 1-12}
```
5-8 gaps. `review_mentions` is a real count over the critical set (or null with the evidence in words). Dataset title must start with "Sample scoring:" and the description must say scores are judgment.
