"""Monthly install history from archived Google Play pages (Internet Archive), so the last 12 months
of real downloads can be shown per app.

  python archive_installs.py --apps <apps.json with appId[, app]> --months 12 --out archive_installs.json

For each app and month it asks the Wayback CDX API for a 200 snapshot of the Play listing, takes the
one closest to the month's end, and reads the exact install count (realInstalls) embedded in the page.
Monthly downloads = difference between consecutive month-end counts, scaled to 30 days. These are
GLOBAL downloads (Play's counter is worldwide). Months without a snapshot are null — never filled in.

Needs network access to web.archive.org. Status: written against the Wayback CDX/id_ endpoints and the
current Play page format; verify on one app before running on many (older pages may lack the field).
"""
import argparse, datetime as dt, json, re, time, urllib.parse, urllib.request

CDX = "https://web.archive.org/cdx/search/cdx"
# Play pages embed installs as e.g. ["1,000,000+",1000000,1514479,"1M+"]: bracket, minInstalls, realInstalls
INSTALLS = re.compile(r'\["([\d.,\s]+\+)",(\d+),(\d+),"[^"]*"\]')


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "market-research/1.0"}), timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def snapshots(pkg, frm, to):
    q = {"url": f"play.google.com/store/apps/details?id={pkg}", "matchType": "prefix", "from": frm, "to": to,
         "output": "json", "fl": "timestamp,original,statuscode", "filter": "statuscode:200"}
    txt = get(CDX + "?" + urllib.parse.urlencode(q))
    if not txt:
        return []
    rows = json.loads(txt)
    return [dict(zip(rows[0], r)) for r in rows[1:]] if rows else []


def real_installs(ts, original):
    html = get(f"https://web.archive.org/web/{ts}id_/{original}")
    if not html:
        return None
    m = INSTALLS.search(html)
    return int(m.group(3)) if m else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apps", required=True)
    p.add_argument("--months", type=int, default=12)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    apps = json.load(open(a.apps))
    today = dt.date.today().replace(day=1)
    months = []
    for k in range(a.months, -1, -1):  # one extra month so the first month has a starting point
        y, mth = today.year, today.month - k
        while mth <= 0:
            mth += 12; y -= 1
        months.append(dt.date(y, mth, 1))
    out = []
    for x in apps:
        pkg = x["appId"]
        snaps = snapshots(pkg, months[0].strftime("%Y%m"), dt.date.today().strftime("%Y%m%d"))
        points = []
        for m0 in months:
            nxt = (m0.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
            in_month = [s for s in snaps if s["timestamp"][:6] == m0.strftime("%Y%m")]
            if not in_month:
                points.append({"month": m0.strftime("%Y-%m"), "snapshot": None, "installs": None}); continue
            target = nxt.strftime("%Y%m%d")
            best = min(in_month, key=lambda s: abs(int(s["timestamp"][:8]) - int(target)))
            points.append({"month": m0.strftime("%Y-%m"), "snapshot": best["timestamp"], "installs": real_installs(best["timestamp"], best["original"])})
            time.sleep(1)
        for prev, cur in zip(points, points[1:]):
            dl = None
            if prev["installs"] is not None and cur["installs"] is not None:
                d0 = dt.datetime.strptime(prev["snapshot"][:8], "%Y%m%d"); d1 = dt.datetime.strptime(cur["snapshot"][:8], "%Y%m%d")
                days = max((d1 - d0).days, 1)
                dl = round((cur["installs"] - prev["installs"]) * 30 / days)
            out.append({"app": x.get("app", pkg), "package": pkg, "month": cur["month"], "installs_month_end": cur["installs"],
                        "snapshot": cur["snapshot"], "downloads_30d": dl})
        print(pkg, [(r["month"], r["downloads_30d"]) for r in out if r["package"] == pkg])
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=0)
    print("saved", a.out)


if __name__ == "__main__":
    main()
