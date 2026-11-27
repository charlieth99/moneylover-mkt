# Category config (references/categories/<name>.json)

```json
{
  "name": "Language learning",
  "genres": ["EDUCATION"],
  "keywords": {"en": ["learn english", "..."], "vi": ["học tiếng anh", "..."], "id": ["belajar bahasa inggris", "..."]},
  "include": "regex that a relevant app's title or short summary matches",
  "exclude": "regex on the title for apps to drop (adjacent categories)",
  "features": {
    "Feature name used as column": {"label": "Label shown on the page (report language)", "pattern": "regex over EN + local listing"}
  },
  "verify_by_hand": ["features that differentiate apps and need reading the snippet"]
}
```

Tips
- 15-35 search keywords per language: how locals actually search, brand names of leaders, plus English terms (many locals search in English).
- `genres` are Play genre ids (FINANCE, EDUCATION, HEALTH_AND_FITNESS, PRODUCTIVITY, LIFESTYLE, TOOLS, BUSINESS, …).
- `exclude` keeps out adjacent categories (for finance: banks, loans, crypto, POS).
- 20-25 features. Put table-stakes features first and differentiators (AI, auto-import, sharing, web) in `verify_by_hand`.
- Feature patterns: avoid short generic words; use `(?-i:...)` for case-sensitive acronyms.
- See `personal-finance.json` for a full example in English, Indonesian and Vietnamese.
