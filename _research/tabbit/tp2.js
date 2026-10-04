// tp2.js — 枚举导航文本 + 探测候选 token 路由
const out = {};
await page.goto('https://app.travelpayouts.com/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(8000);

// 1) 侧栏/导航可见文本（去重）
const raw = await page.evaluate(() =>
  Array.from(document.querySelectorAll('a,[role="link"],nav li,aside *,[class*="menu" i] li,[class*="sidebar" i] *'))
    .map(e => (e.textContent || '').trim())
    .filter(t => t && t.length > 0 && t.length < 40)
);
out.nav = [...new Set(raw)].slice(0, 80);

// 2) 同源 fetch 探测候选路由（跟随重定向后仍是 200 才算存在）
out.probes = await page.evaluate(async () => {
  const candidates = [
    '/api_tokens', '/dashboard/api_tokens', '/tokens', '/dashboard/tokens',
    '/profile/api', '/settings/api', '/api-token', '/dashboard/api-token',
    '/account/api', '/marker', '/markers'
  ];
  const res = [];
  for (const c of candidates) {
    try {
      const r = await fetch('https://app.travelpayouts.com' + c, { redirect: 'follow' });
      const text = await r.text();
      res.push({
        c, status: r.status, final: r.url,
        hasTokenLike: /\b[a-f0-9]{32}\b/i.test(text),
        snippet: r.ok ? (text.match(/api[_ ]?token[\s\S]{0,120}/i) || [''])[0].slice(0, 150) : ''
      });
    } catch (e) { res.push({ c, err: String(e).slice(0, 80) }); }
  }
  return res;
});
return out;
