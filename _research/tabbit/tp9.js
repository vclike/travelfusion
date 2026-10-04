// tp9.js — 按官方截图路径取 token：头像 → Profile → API tokens → 读值（绝不点 Update token）
const fs = await import('node:fs');
const out = {};
await page.goto('https://app.travelpayouts.com/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(6000);

// 1) 点开右上角账户菜单（依次尝试头部图标按钮）
const btns = await page.$$('header button, [class*="header" i] button, button[class*="icon" i], button[class*="avatar" i]');
out.tried = btns.length;
for (const b of btns.slice(0, 6)) {
  try {
    await b.click({ timeout: 2000 });
    await page.waitForTimeout(1500);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Profile|Log out|Dark mode/i.test(t)) { out.opened = true; break; }
  } catch (e) { /* 下一个 */ }
}

// 2) 点 Profile 菜单项
try {
  const prof = page.getByText(/^Profile$/i, { exact: true }).first();
  if (await prof.count()) { await prof.click({ timeout: 3000 }); await page.waitForTimeout(4000); }
  else out.noProfileItem = true;
} catch (e) { out.profileErr = String(e).slice(0, 100); }
out.urlProfile = page.url();

// 3) 点左侧 API tokens 标签
try {
  const tab = page.getByText(/api\s*tokens?/i, { exact: false }).first();
  if (await tab.count()) { await tab.click({ timeout: 3000 }); await page.waitForTimeout(3000); }
} catch (e) { out.tabErr = String(e).slice(0, 100); }
out.urlToken = page.url();

// 4) 提取 token：input 值优先 + 32-40 位 hex 兜底
const data = await page.evaluate(() => {
  const inputs = Array.from(document.querySelectorAll('input, [class*="token" i] code, code'))
    .map(i => (i.value || i.textContent || '').trim())
    .filter(v => /^[a-f0-9]{16,64}$/i.test(v));
  const hexes = (document.body.innerText.match(/\b[a-f0-9]{32,40}\b/g) || []);
  return { inputs: [...new Set(inputs)], hexes: [...new Set(hexes)],
           pageText: document.body.innerText.slice(0, 600) };
});
out.tokenInputs = data.inputs;
out.hexOnPage = data.hexes;

const payload = { url: out.urlToken, inputs: data.inputs, hexes: data.hexes,
                  at: new Date().toISOString() };
fs.writeFileSync('D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/_research/tabbit/tp_token.txt',
  JSON.stringify(payload, null, 2));
out.pageHead = data.pageText;
return out;
