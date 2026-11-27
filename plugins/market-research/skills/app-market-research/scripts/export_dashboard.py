"""Turn analysis.json + your hand-made corrections into the dashboard's data files.

  python export_dashboard.py --dir DIR --category ../references/categories/<cat>.json --edits edits.json --out OUTDIR

edits.json (written by you after reading feature_snippets.txt and the listings):
{
  "short_names": {"com.bookmark.money": "Money Lover", ...},          # short label per app (optional)
  "local_developers": ["com.finku", ...],                              # apps built by a local company
  "features": {"com.finku": {"Receipt scan": "yes", "Web / desktop version": "partial", "Calendar view": "no"}},
  "focal_app": "com.bookmark.money"                                    # the app the opportunity section is about (optional)
}
Writes OUTDIR/apps.json, features.json, sentiment.json, themes.json — upload each as a dashboard file.
"""
import argparse, json, os


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--edits", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    an = json.load(open(f"{a.dir}/analysis.json"))
    apps = {x["appId"]: x for x in json.load(open(f"{a.dir}/apps.json"))}
    cat, ed = json.load(open(a.category)), json.load(open(a.edits))
    os.makedirs(a.out, exist_ok=True)
    names, local = ed.get("short_names", {}), set(ed.get("local_developers", []))
    ends = an["window_ends"]
    out_apps, sent = [], []
    for i, r in enumerate(an["top"], 1):
        x = apps[r["appId"]]
        row = {"rank": i, "app": names.get(r["appId"], x["title"]), "play_title": x["title"], "developer": x["developer"],
               "package": r["appId"], "built_locally": "Yes" if r["appId"] in local else "No",
               "local_reviews_30d": r["reviews_30d"], "global_installs": x["installs"] or 0,
               "rating": round(x["score"] or 0, 2), "ads": "Yes" if x["ads"] else "No",
               "price_range": (x["iap_range"] or "").replace(" per item", "").replace(" mỗi mục", ""),
               "last_updated": x["updated"], "is_focal": "Yes" if r["appId"] == ed.get("focal_app") else "No"}
        for e, v in zip(ends, r["windows"]):
            row["reviews_to_" + e] = v
        feats = dict(r["features"])
        feats.update(ed.get("features", {}).get(r["appId"], {}))
        for f in cat["features"]:
            row[f] = feats.get(f, "no")
        out_apps.append(row)
        sent.append({"app": row["app"], "package": r["appId"], "reviews_period": r["reviews_period"], "positive": r["positive"],
                     "neutral": r["neutral"], "negative": r["negative"], "avg_stars": r["avg_stars"],
                     "positive_pct": round(r["positive"] / max(r["reviews_period"], 1) * 100, 1),
                     "negative_pct": round(r["negative"] / max(r["reviews_period"], 1) * 100, 1),
                     "dev_reply_to_negative_pct": r["dev_reply_to_negative_pct"], "short_review_pct": r["short_review_pct"],
                     "duplicate_text_pct": r["duplicate_text_pct"], "top_complaint": r["top_complaint"]})
    features = [{"feature": f, "label": spec["label"]} for f, spec in cat["features"].items()]
    for name, data in (("apps", out_apps), ("features", features), ("sentiment", sent), ("themes", an["themes"])):
        json.dump(data, open(f"{a.out}/{name}.json", "w"), ensure_ascii=False, indent=0)
    json.dump({"window_ends": ends, **an["meta"], "counts": an["counts"]}, open(f"{a.out}/meta.json", "w"), ensure_ascii=False, indent=1)
    print("wrote", ", ".join(f"{a.out}/{n}.json" for n in ("apps", "features", "sentiment", "themes", "meta")))


if __name__ == "__main__":
    main()
