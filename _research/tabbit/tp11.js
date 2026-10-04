// tp11.js — 控制台已解锁：头像 → Profile → API tokens → 提取 token（不碰 Update token）
const fs = await import('node:fs');
const out = {};
await page.goto('https://app.travelpayouts.com/drive?source=579428', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(5000);
out.url1 = page.url();

// 1) 打开账户下拉菜单
const btns = await page.$$('header button, [class*="header" i] button, button[class*="avatar" i], [class*="account" i] button, button');
let opened = false;
for (const b of btns.slice(0, 8)) {
  try {
    await b.click({ timeout: 2000 });
    await page.waitForTimeout(1200);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Profile|My Projects|Referral program/i.test(t)) { opened = true; break; }
  } catch (e) { /* 下一个 */ }
}
out.menuOpened = opened;

// 2) 点 Profile
try {
  const prof = page.getByText(/^Profile$/i).first();
  if (await prof.count()) { await prof.click({ timeout: 3000 }); await page.waitForTimeout(4000); }
  else out.noProfileItem = true;
} catch (e) { out.profErr = String(e).slice(0, 80); }
out.url2 = page.url();

// 3) 点 API tokens 标签
try {
  const tab = page.getByText(/API tokens?/i).first();
  if (await tab.count()) { await tab.click({ timeout: 3000 }); await page.waitForTimeout(3000); }
} catch (e) { out.tabErr = String(e).slice(0, 80); }
out.url3 = page.url();

// 4) 提取 token：input 值优先 + hex 兜底
const data = await page.evaluate(() => {
  const inputs = Array.from(document.querySelectorAll('input'))
    .map(i => (i.value || '').trim())
    .filter(v => v.length >= 20);
  const hexes = (document.body.innerText.match(/\b[a-f0-9]{32,40}\b/g) || []);
  return { inputs: [...new Set(inputs)], hexes: [...new Set(hexes)],
           text: document.body.innerText.slice(0, 700) };
});
out.tokenInputs = data.inputs;
out.hexes = data.hexes;
out.pageText = data.text;

fs.writeFileSync('D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/_research/tabbit/tp_token.txt',
  JSON.stringify({ url: out.url3, inputs: data.inputs, hexes: data.hexes,
                   at: new Date().toISOString() }, null, 2));
return out;
