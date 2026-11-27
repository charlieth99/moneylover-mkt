"""Crawl Google Play for one app category in one country.

  python crawl.py --country vn --lang vi --category ../references/categories/personal-finance.json --out DIR
      [--months 6] [--min-installs 10000] [--max-pages 25] [--extra-apps pkg1,pkg2]

Writes DIR/apps.json (listing details, local + English descriptions) and DIR/reviews.json
(reviews of the last N months that look written in the local language; no reviewer names).
Needs: pip install google-play-scraper
"""
import argparse, datetime as dt, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import langs  # noqa: E402
from google_play_scraper import app, reviews, search, Sort  # noqa: E402

NOW = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def retry(fn, *a, **k):
    for i in range(3):
        try:
            return fn(*a, **k)
        except Exception as e:
            if "not found" in str(e).lower():
                return None
            time.sleep(2 * (i + 1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--country", required=True)
    p.add_argument("--lang", required=True, help="language profile in langs.py, e.g. vi, id")
    p.add_argument("--category", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--months", type=int, default=6)
    p.add_argument("--min-installs", type=int, default=10_000)
    p.add_argument("--max-pages", type=int, default=25)
    p.add_argument("--extra-apps", default="", help="comma-separated package ids to always include (e.g. the focal app)")
    a = p.parse_args()
    prof = langs.get(a.lang)
    cat = json.load(open(a.category))
    inc, exc = re.compile(cat["include"], re.I), re.compile(cat["exclude"], re.I)
    os.makedirs(a.out, exist_ok=True)

    ids = {}
    for lang in [prof["play_lang"], "en"]:
        for kw in cat["keywords"].get(lang, []):
            for r in retry(search, kw, lang=lang, country=a.country, n_hits=30) or []:
                ids.setdefault(r["appId"], set()).add(kw)
            time.sleep(0.3)
    extra = [x for x in a.extra_apps.split(",") if x]
    for x in extra:
        ids.setdefault(x, set()).add("(extra)")
    print("search hits", len(ids), flush=True)

    def detail(app_id):
        loc = retry(app, app_id, lang=prof["play_lang"], country=a.country)
        if not loc:
            return None
        forced = app_id in extra
        if not forced:
            if loc.get("genreId") not in cat["genres"]:
                return None
            if not inc.search(f"{loc.get('title','')} {loc.get('summary','')}") or exc.search(loc.get("title", "")):
                return None
        en = retry(app, app_id, lang="en", country=a.country) or {}
        return {"appId": app_id, "title": loc["title"], "title_en": en.get("title"), "developer": loc["developer"],
                "developer_address": loc.get("developerAddress"), "genre": loc.get("genreId"),
                "installs": loc.get("realInstalls"), "installs_bracket": loc.get("installs"), "ratings": loc.get("ratings"),
                "reviews_total": loc.get("reviews"), "score": loc.get("score"), "ads": loc.get("containsAds"),
                "iap": loc.get("offersIAP"), "iap_range": loc.get("inAppProductPrice"), "updated": loc.get("lastUpdatedOn"),
                "url": loc.get("url"), "summary": loc.get("summary"), "desc_local": loc.get("description"),
                "desc_en": en.get("description"), "keywords": sorted(ids[app_id])}

    with ThreadPoolExecutor(6) as ex:
        apps = [x for x in ex.map(detail, ids) if x]
    apps.sort(key=lambda x: -(x["installs"] or 0))
    print("category apps", len(apps), flush=True)

    since = NOW - dt.timedelta(days=30 * a.months)

    def collect(x):
        out, token = [], None
        for _ in range(a.max_pages):
            res = retry(reviews, x["appId"], lang=prof["play_lang"], country=a.country, sort=Sort.NEWEST,
                        count=200, continuation_token=token)
            if not res or not res[0]:
                break
            batch, token = res
            out += batch
            if batch[-1]["at"] < since or token is None:
                break
        else:
            x["review_sample_capped"] = True
        x["review_sample_oldest"] = min((r["at"] for r in out), default=NOW).strftime("%Y-%m-%d")
        return [{"appId": x["appId"], "score": r["score"], "at": r["at"].strftime("%Y-%m-%d"),
                 "thumbs": r.get("thumbsUpCount") or 0, "version": r.get("reviewCreatedVersion"),
                 "dev_replied": bool(r.get("replyContent")), "text": r["content"] or ""}
                for r in out if r["at"] >= since and prof["is_local"](r["content"])]

    big = [x for x in apps if (x["installs"] or 0) >= a.min_installs or x["appId"] in extra]
    with ThreadPoolExecutor(6) as ex:
        allrev = [r for rows in ex.map(collect, big) for r in rows]
    json.dump(apps, open(f"{a.out}/apps.json", "w"), ensure_ascii=False, indent=0)
    json.dump(allrev, open(f"{a.out}/reviews.json", "w"), ensure_ascii=False, indent=0)
    json.dump({"country": a.country, "lang": a.lang, "category": cat["name"], "months": a.months,
               "crawled_at": NOW.strftime("%Y-%m-%d"), "extra_apps": extra},
              open(f"{a.out}/crawl_meta.json", "w"), ensure_ascii=False, indent=1)
    print(f"saved {len(apps)} apps, {len(allrev)} local-language reviews -> {a.out}")


if __name__ == "__main__":
    main()
