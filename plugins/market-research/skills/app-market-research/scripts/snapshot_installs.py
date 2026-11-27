"""Snapshot exact Google Play install counts so real downloads can be computed as deltas.

  python snapshot_installs.py --apps <DIR>/apps.json --country vn --out <SNAPSHOT_DIR> [--top 50]
  python snapshot_installs.py --deltas <SNAPSHOT_DIR>          # prints downloads between first and last snapshot

Run daily (e.g. a scheduled task) and keep SNAPSHOT_DIR somewhere durable (a repo branch), since
cloud sandboxes are wiped. realInstalls is worldwide, so a delta is global downloads: close to local
only for apps whose users are mostly in that market.
"""
import argparse, csv, datetime as dt, glob, json, os, time
from concurrent.futures import ThreadPoolExecutor


def snap(a):
    from google_play_scraper import app
    os.makedirs(a.out, exist_ok=True)
    ids = [x["appId"] for x in json.load(open(a.apps))][: a.top]

    def one(i):
        for k in range(3):
            try:
                return i, app(i, lang="en", country=a.country).get("realInstalls")
            except Exception:
                time.sleep(2 * (k + 1))
        return i, None

    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(one, ids))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M")
    with open(f"{a.out}/{now}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["appId", "realInstalls"]); w.writerows(rows)
    print("saved", f"{a.out}/{now}.csv")


def deltas(d):
    files = sorted(glob.glob(f"{d}/*.csv"))
    if len(files) < 2:
        raise SystemExit("need at least two snapshots")
    read = lambda p: {r["appId"]: int(r["realInstalls"]) for r in csv.DictReader(open(p)) if r["realInstalls"]}
    first, last = read(files[0]), read(files[-1])
    t0 = dt.datetime.strptime(os.path.basename(files[0])[:-4], "%Y-%m-%dT%H%M")
    t1 = dt.datetime.strptime(os.path.basename(files[-1])[:-4], "%Y-%m-%dT%H%M")
    days = max((t1 - t0).total_seconds() / 86400, 1e-9)
    print(f"{files[0]} -> {files[-1]} ({days:.1f} days)")
    for i in sorted(last, key=lambda i: -(last[i] - first.get(i, last[i]))):
        if i in first:
            n = last[i] - first[i]
            print(f"{i:<50} {n:>10,}  ({n / days * 30:,.0f} per 30 days)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--apps"); p.add_argument("--country", default="us"); p.add_argument("--out")
    p.add_argument("--top", type=int, default=50); p.add_argument("--deltas")
    a = p.parse_args()
    deltas(a.deltas) if a.deltas else snap(a)
