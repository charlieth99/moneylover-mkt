"""Rank apps by local review activity and prepare everything the report needs.

  python analyze.py --dir DIR --category ../references/categories/<cat>.json --lang vi [--top 20]

Reads DIR/apps.json, DIR/reviews.json. Writes DIR/analysis.json and, for reading by hand,
DIR/feature_snippets.txt (matched listing text per feature, to confirm or correct) and
DIR/review_samples.txt (all 1-2 star reviews + a sample of mixed/wish reviews, to pick quotes).
"""
import argparse, collections as C, datetime as dt, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import langs  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--lang", required=True)
    p.add_argument("--top", type=int, default=20)
    p.add_argument("--exclude-apps", default="", help="comma-separated package ids to drop after reading the list (e.g. a full banking app)")
    a = p.parse_args()
    prof, cat = langs.get(a.lang), json.load(open(a.category))
    meta = json.load(open(f"{a.dir}/crawl_meta.json"))
    now = dt.datetime.strptime(meta["crawled_at"], "%Y-%m-%d") + dt.timedelta(days=1)
    apps = {x["appId"]: x for x in json.load(open(f"{a.dir}/apps.json"))}
    drop = {x for x in a.exclude_apps.split(",") if x}
    apps = {k: v for k, v in apps.items() if k not in drop}
    revs = [r for r in json.load(open(f"{a.dir}/reviews.json")) if r["appId"] not in drop]
    meta["excluded_apps"] = sorted(drop)
    cat_th = cat.get("themes", {}).get(a.lang)
    if cat_th:  # a category can bring its own themes for a language (e.g. "speech recognition is wrong")
        prof = dict(prof, themes=cat_th["themes"], n_complaint=cat_th["n_complaint"])
    contrast, wish = re.compile(prof["contrast"], re.I), re.compile(prof["wish"], re.I)
    theme_names = list(prof["themes"])
    by = C.defaultdict(list)
    for r in revs:
        r["themes"] = [t for t, pat in prof["themes"].items() if re.search(pat, r["text"], re.I)]
        by[r["appId"]].append(r)

    ends = [now - dt.timedelta(days=30 * m) for m in range(meta["months"])][::-1]
    rows = []
    for aid, x in apps.items():
        rs = by.get(aid, [])
        n30 = sum(r["at"] >= (now - dt.timedelta(days=30)).strftime("%Y-%m-%d") for r in rs)
        if x.get("review_sample_capped") and rs:
            span = (now - dt.datetime.strptime(min(r["at"] for r in rs), "%Y-%m-%d")).days
            if span < 30:
                n30 = round(len(rs) * 30 / max(span, 1))
        oldest = x.get("review_sample_oldest") if x.get("review_sample_capped") else None
        # a capped sample doesn't reach back far enough: windows it doesn't fully cover are unknown, not zero
        win = [None if oldest and (e - dt.timedelta(days=30)).strftime("%Y-%m-%d") < oldest else
               sum((e - dt.timedelta(days=30)).strftime("%Y-%m-%d") <= r["at"] < e.strftime("%Y-%m-%d") for r in rs) for e in ends]
        rows.append({"appId": aid, "reviews_30d": n30, "windows": win, "reviews_period": len(rs),
                     "capped": bool(x.get("review_sample_capped"))})
    rows.sort(key=lambda r: (-r["reviews_30d"], -r["reviews_period"]))
    top = rows[: a.top]
    for extra in meta.get("extra_apps", []):
        if extra in apps and extra not in {r["appId"] for r in top}:
            top.append(next(r for r in rows if r["appId"] == extra))

    snip = open(f"{a.dir}/feature_snippets.txt", "w")
    for r in top:
        x = apps[r["appId"]]
        text = " ".join(filter(None, [x.get("title"), x.get("summary"), x.get("desc_local"), x.get("desc_en")]))
        r["features"] = {}
        for f, spec in cat["features"].items():
            m = re.search(spec["pattern"], text, re.I)
            r["features"][f] = "yes" if m else "no"
            if m and f in cat.get("verify_by_hand", []):
                ctx = " ".join(text[max(0, m.start() - 90): m.end() + 90].split())
                snip.write(f"[{r['appId']}] {f} <<{m.group(0)}>>: ...{ctx}...\n")
        rs = by.get(r["appId"], [])
        n = len(rs) or 1
        neg = [y for y in rs if y["score"] <= 2]
        cnt = C.Counter(y["text"].lower().strip() for y in rs)
        pain = [y for y in rs if y["score"] <= 3 or (contrast.search(y["text"]) and len(y["text"]) > 40)]
        comp = C.Counter(t for y in pain for t in y["themes"] if t in theme_names[: prof["n_complaint"]])
        r.update(positive=sum(y["score"] >= 4 for y in rs), negative=len(neg), neutral=len(rs) - len(neg) - sum(y["score"] >= 4 for y in rs),
                 avg_stars=round(sum(y["score"] for y in rs) / n, 2),
                 dev_reply_to_negative_pct=round(sum(y["dev_replied"] for y in neg) / len(neg) * 100) if neg else None,
                 short_review_pct=round(sum(len(y["text"]) <= 20 for y in rs) / n * 100),
                 duplicate_text_pct=round(sum(v for v in cnt.values() if v > 1) / n * 100),
                 top_complaint=comp.most_common(1)[0][0] if comp else None)
    snip.close()

    ids = {r["appId"] for r in top}
    pool = [y for y in revs if y["appId"] in ids]
    pain = [y for y in pool if y["score"] <= 3 or (y["score"] >= 4 and contrast.search(y["text"]) and len(y["text"]) > 40)]
    pos = [y for y in pool if y["score"] >= 4]
    themes = [{"theme": t, "kind": "complaint" if i < prof["n_complaint"] else "praise",
               "critical_reviews": sum(t in y["themes"] for y in pain),
               "negative_reviews": sum(t in y["themes"] for y in pool if y["score"] <= 2),
               "positive_reviews": sum(t in y["themes"] for y in pos)} for i, t in enumerate(theme_names)]

    title = {k: v["title"] for k, v in apps.items()}
    with open(f"{a.dir}/review_samples.txt", "w") as f:
        f.write("# 1-2 star reviews\n")
        for y in sorted((y for y in pool if y["score"] <= 2), key=lambda y: (y["appId"], y["at"])):
            f.write(f"[{title[y['appId']][:24]}|{y['score']}★|{y['at']}] {y['text'][:240]}\n")
        f.write("\n# 4-5 star reviews with a 'but' or a wish (sample)\n")
        mixed = [y for y in pos if (contrast.search(y["text"]) or wish.search(y["text"])) and len(y["text"]) > 40]
        random.seed(7)
        for y in random.sample(mixed, min(120, len(mixed))):
            f.write(f"[{title[y['appId']][:24]}|{y['score']}★|{y['at']}] {y['text'][:240]}\n")
    json.dump({"meta": meta, "window_ends": [(e - dt.timedelta(days=1)).strftime("%Y-%m-%d") for e in ends], "top": top, "themes": themes,
               "counts": {"reviews_top": len(pool), "critical_set": len(pain), "positive": len(pos)}},
              open(f"{a.dir}/analysis.json", "w"), ensure_ascii=False, indent=1)
    print(f"top {len(top)} apps; {len(pool)} reviews; critical set {len(pain)}")
    for i, r in enumerate(top, 1):
        print(f"{i:>2} {r['reviews_30d']:>5}/30d {r['reviews_period']:>5}/period  {title[r['appId']][:40]}  ({r['appId']})")


if __name__ == "__main__":
    main()
