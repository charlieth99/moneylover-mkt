"""Fill assets/dashboard_page.html into a ready-to-upload page.

  python fill_page.py --values values.json --out <DIR>/dash [--no-focal]

values.json:
{
  "placeholders": {"TITLE": "...", "MARKET": "...", "LANG_ADJ": "...", "CATEGORY": "...", "CRAWL_DATE": "...",
                   "WINDOW": "...", "FOCAL": "...", "LOCAL_DEV": "...", "FOREIGN_DEV": "...",
                   "GAPS_TITLE": "...", "FIT_LABEL": "...", "HAS_LABEL": "..."},
  "blocks": {"REVIEW_FINDINGS": "<li>…</li>…", "FOCAL_VERDICT": "…", "FOCAL_SUMMARY": "…", "RISKS": "<li>…</li>…"},
  "replace": [["exact text in the template", "new text"]]      # optional, for market-specific wording
}
Writes <out>/index.html and <out>/files_index.json ({"text": ...}, the dashboard's files/index.html document),
and fails if any placeholder or WRITE block is left. Check the script with: node --check <out>/page_script.js
"""
import argparse, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--values", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-focal", action="store_true", help="drop the focal-app verdict and comparison")
    a = p.parse_args()
    v = json.load(open(a.values))
    t = open(os.path.join(HERE, "..", "assets", "dashboard_page.html")).read()
    t = re.sub(r"<!--\n  App market research page.*?-->\n", "", t, count=1, flags=re.S)
    if a.no_focal:
        t = re.sub(r'\n    <div id="focal-position" class="amr-section">.*?</div><!-- /focal-position -->', "", t, count=1, flags=re.S)
        v.setdefault("blocks", {}).setdefault("FOCAL_VERDICT", "")
        v["blocks"].setdefault("FOCAL_SUMMARY", "")
    for old, new in v.get("replace", []):
        if old not in t:
            raise SystemExit(f"replace: text not found in template: {old[:60]}")
        t = t.replace(old, new)
    for k, val in v.get("placeholders", {}).items():
        t = t.replace("{{" + k + "}}", val)
    for k, val in v.get("blocks", {}).items():
        t = re.sub(r"<!-- WRITE:" + k + r"\b.*?-->", lambda m: val, t, count=1)
    left = sorted(set(re.findall(r"\{\{\w+\}\}|WRITE:\w+", t)))
    if left:
        raise SystemExit(f"still to fill: {left}")
    os.makedirs(a.out, exist_ok=True)
    open(f"{a.out}/index.html", "w").write(t)
    json.dump({"text": t}, open(f"{a.out}/files_index.json", "w"), ensure_ascii=False)
    open(f"{a.out}/page_script.js", "w").write(re.search(r"<script>(.*)</script>", t, re.S).group(1))
    print("wrote", f"{a.out}/index.html", f"{a.out}/files_index.json")


if __name__ == "__main__":
    main()
