// Paste into the DevTools console (F12 → Console) on a web.archive.org tab, then press Enter.
// Read-only: it fetches archived Google Play pages from web.archive.org (same site) and reads the
// exact install count in each. Takes ~15-25 minutes for 20 apps. At the end it downloads
// archive_installs_raw.json and copies the same text to the clipboard.
(async () => {
  const apps = __APPS__;
  const MONTHS = 12;
  const now = new Date();
  const months = [];
  for (let k = MONTHS; k >= 0; k--) {
    const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - k, 1));
    months.push(d.toISOString().slice(0, 7).replace('-', ''));
  }
  const re = /\["([\d.,\s]+\+)",(\d+),(\d+),"[^"]*"\]/;
  const out = [];
  for (const [i, pkg] of apps.entries()) {
    console.log(`(${i + 1}/${apps.length}) ${pkg}`);
    let rows = [];
    try {
      const q = new URLSearchParams({ url: `play.google.com/store/apps/details?id=${pkg}`, matchType: 'prefix',
        from: months[0], output: 'json', fl: 'timestamp,original', filter: 'statuscode:200' });
      const j = await (await fetch('/cdx/search/cdx?' + q)).json();
      rows = j.slice(1);
    } catch (e) { console.warn(pkg, 'không đọc được danh sách bản lưu', e); }
    for (const m of months) {
      const inMonth = rows.filter(([ts]) => ts.startsWith(m));
      if (!inMonth.length) { out.push({ package: pkg, month: m, snapshot: null, installs: null }); continue; }
      let installs = null, snap = null;
      for (const [ts, orig] of inMonth.slice(-3).reverse()) {   // newest of the month first, up to 3 tries
        try {
          const h = await (await fetch(`/web/${ts}id_/${orig}`)).text();
          const mm = h.match(re);
          if (mm) { installs = +mm[3]; snap = ts; break; }
        } catch (e) { /* try the next snapshot */ }
        await new Promise((r) => setTimeout(r, 400));
      }
      out.push({ package: pkg, month: m, snapshot: snap, installs });
    }
  }
  const text = JSON.stringify(out);
  try { copy(text); console.log('Đã copy kết quả vào clipboard'); } catch (e) {}
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
  a.download = 'archive_installs_raw.json';
  a.click();
  console.log('Xong:', out.filter((x) => x.installs).length, '/', out.length, 'tháng có số lượt cài');
})();
