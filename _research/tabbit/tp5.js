// tp5.js — 找真正的 Profile/Account 设置区（API token 标签所在）
const out = {};
await page.goto('https://app.travelpayouts.com/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(6000);

// 同源探测更多候选路由
out.probes = await page.evaluate(async () => {
  const candidates = [
    '/account', '/my-account', '/settings', '/profile/settings',
    '/profile/api-token', '/profile?tab=api-token', '/account/profile',
    '/account/settings', '/profile/edit', '/user/profile'
  ];
  const res = [];
  for (const c of candidates) {
    try {
      const r = await fetch('https://app.travelpayouts.com' + c, { redirect: 'follow' });
      const text = await r.text();
      res.push({
        c, status: r.status, final: r.url,
        hasTokenLike: /\b[a-f0-9]{32,40}\b/i.test(text),
        hasApiTokenText: /api\s*token/i.test(text)
      });
    } catch (e) { res.push({ c, err: String(e).slice(0, 60) }); }
  }
  return res;
});

// 头像/账户菜单：列出页面右上区域可点击文本
out.clickables = await page.evaluate(() => {
  const els = Array.from(document.querySelectorAll('button, a, [role="button"], img[alt], [class*="avatar" i], [class*="user" i]'))
    .map(e => ({ tag: e.tagName, t: (e.textContent || e.alt || '').trim().slice(0, 40), cls: (e.className || '').toString().slice(0, 60) }))
    .filter(x => x.t || x.cls);
  return els.slice(0, 50);
});
return out;
