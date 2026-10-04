// tp6.js — www 主站控制台尝试 + 全文关键区扫描
const out = {};
await page.goto('https://travelpayouts.com/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(8000);
out.finalUrl = page.url();
out.title = await page.title();
const text = await page.evaluate(() => document.body.innerText);
out.textHead = text.slice(0, 1800);
out.keySections = [...new Set(text.match(/(Profile|API token|Statistics|Payouts|Programs|Account|Settings|Dashboard|Drive)/gi) || [])];
out.hasToken = /\b[a-f0-9]{32,40}\b/.test(text);
return out;
