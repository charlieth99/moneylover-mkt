"""Turn install snapshots (from snapshot_installs.py) into the dashboard's `installs` dataset.

  python installs_to_dashboard.py --snapshots <SNAPSHOT_DIR> --apps <apps.json with appId, app> --out installs.json

One row per app and snapshot: {app, package, snapshot_at (ISO UTC), installs, downloads_since_first, changed}.
`changed` is "No" while Google still shows the first snapshot's count: Play refreshes realInstalls
per app every few days, so an unchanged count means "not refreshed yet", never "zero downloads".
"""
import argparse, csv, datetime as dt, glob, json, os


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshots", required=True)
    p.add_argument("--apps", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    names = {x["appId"]: x.get("app") or x["appId"] for x in json.load(open(a.apps))}
    snaps = []
    for f in sorted(glob.glob(f"{a.snapshots}/*.csv")):
        at = dt.datetime.strptime(os.path.basename(f)[:-4], "%Y-%m-%dT%H%M").strftime("%Y-%m-%dT%H:%M:00Z")
        vals = {r["appId"]: int(r["realInstalls"]) for r in csv.DictReader(open(f)) if r.get("realInstalls")}
        snaps.append((at, vals))
    rows, first = [], {}
    for at, vals in snaps:
        for pkg, n in vals.items():
            if pkg not in names:
                continue
            first.setdefault(pkg, n)
            rows.append({"app": names[pkg], "package": pkg, "snapshot_at": at, "installs": n,
                         "downloads_since_first": n - first[pkg], "changed": "Yes" if n != first[pkg] else "No"})
    json.dump(rows, open(a.out, "w"), ensure_ascii=False, indent=0)
    print(f"{len(rows)} rows from {len(snaps)} snapshots -> {a.out}")


if __name__ == "__main__":
    main()
