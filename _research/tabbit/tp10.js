// tp10.js — 双测：验证页可达性 + 控制面板解锁状态
const out = {};
// 1) 验证页
try {
  const resp = await page.goto('https://tp.jasonkiu.com/?init_marker=783555&init_trs=579428&init_locale=en',
    { waitUntil: 'domcontentloaded', timeout: 30000 });
  out.tpStatus = resp ? resp.status() : null;
  await page.waitForTimeout(1500);
  out.tpTitle = await page.title();
  out.tpHasScript = await page.evaluate(() => !!document.querySelector('script[src*="tpembars"]'));
  out.tpHead = (await page.evaluate(() => document.body.innerText || '')).slice(0, 150);
} catch (e) { out.tpErr = String(e).slice(0, 160); }

// 2) 控制面板状态
await page.goto('https://app.travelpayouts.com/dashboard', { waitUntil: 'domcontentloaded', timeout: 45000 });
await page.waitForTimeout(6000);
out.dashUrl = page.url();
const dt = await page.evaluate(() => document.body.innerText);
out.dashState = /Install Drive|Check Drive connection/i.test(dt) ? 'wizard-still-blocking'
  : /Log out/i.test(dt) ? 'maybe-unlocked' : 'unknown';
out.dashHead = dt.slice(0, 400);
// 若已解锁，找头像/Profile 入口线索
out.menuHits = [...new Set((dt.match(/Profile|My account|API token/gi) || []))];
return out;
