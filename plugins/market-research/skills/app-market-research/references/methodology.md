# Methodology and lessons learned

## Metrics
| Metric | Source | What it is | What it is not |
|---|---|---|---|
| Local reviews / 30 days | Play review feed, `lang=<local>`, newest first, filtered by `langs.<lang>.is_local` | Count of reviews written in the market's language in the last 30 days | Downloads; it undercounts users who write in English or one word |
| 6 monthly windows | same | Momentum per app | Seasonality-adjusted anything |
| Global installs | `realInstalls` on the listing | Exact lifetime installs, worldwide | Per-country installs |
| Positive / negative | star rating: 4-5 / 1-2 (3 = neutral) | Sentiment by stars | Text sentiment |
| Critical set | 1-3★ reviews + 4-5★ reviews containing a contrast word ("but") and >40 chars | Where complaints actually live (most reviews are 5★) | — |
| Themes | keyword regex per language profile | Rough topic counts; a review can hit several | Precise classification |
| Features | keyword regex on EN + local listing, then hand-corrected | What the listing claims | Verified in-app behaviour; blank = "not mentioned" |
| Gap scores | Claude's judgment from the above | Prioritisation aid | Measurement |

## Traps found the hard way
- **Neighbour languages leak in.** Google returns Malay reviews under `lang=id`. The Indonesian profile separates them with marker words (tak, boleh, sikit… vs gak, banget, aja…). Do the same for any language with a close neighbour (Thai/Lao, Spanish/Portuguese, Hindi/Urdu in Latin script).
- **Short words that collide.** Vietnamese "ai" (who) matched the AI feature; "máy tính" (calculator keyboard) matched "desktop". Use case-sensitive `(?-i:\bAI\b)` and avoid generic words in feature patterns.
- **Review gating.** A leader with ~0% 1-2★, >40% reviews ≤20 chars and >30% identical texts ("bagus", "mantap", "tốt") is probably showing the review prompt only to happy users. Report it as a likely signal, and don't treat its stars as a benchmark.
- **Install brackets and release dates are unreliable** for monthly estimates; don't divide installs by age.
- **Global apps inflate per-review ratios.** If you ever convert reviews to downloads, cap installs-per-review at a percentile of local apps — but the user preferred counts over estimates, so only do this when asked and label it as an estimate.
- **Snippets with newlines** hide the matched word; analyze.py now prints the match in `<<…>>` on one line.
- **Bank and wallet super-apps slip in** when their listing mentions budgeting (K PLUS in Thailand had 70% of all reviews). Drop them with `analyze.py --exclude-apps` and say so; but keep bank-built *standalone* money apps (MAKE by KBank, Kept by Krungsri) — those are real competitors and a key finding.
- **Capped samples in big markets.** A top US app gets thousands of reviews a month, so 40 pages may cover only weeks. The 30-day count is then extrapolated from the sample's span and older windows are `null`; don't read a missing month as a drop.
- **Generalist apps distort a niche.** In the US, Duolingo's English reviews come mostly from English speakers learning other languages; keep it out of an English-learning category unless the market is one where it is mainly used to learn English.
- **Keyword coverage** decides what's in the list. Check that known leaders are present; add `--extra-apps` for the focal app and anything the user names.
- **Cloud sandboxes** often block the App Store, AppTweak and Similarweb. Say what was blocked; don't fill gaps from memory.

- **Changing the crawl changes the counts.** The first Indonesia report also counted Indonesian-written reviews found under the English feed; the skill reads only the local feed, so its monthly numbers run a little lower. Don't mix the two in one chart without saying so.

## Honesty rules the user asked for
- Say where every number comes from. Separate data from judgment on the page and in chat.
- Don't call reviews downloads. Don't call global installs local.
- When a claim is a hypothesis (e.g. "bank apps absorbed this market"), say it's a hypothesis and what would check it.
