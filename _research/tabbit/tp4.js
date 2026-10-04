// tp4.js — Profile → API token 标签 → 提取 token（绝不点 Update token！）
const fs = await import('node:fs');
const out = {};
await page.goto('https://app.travelpayouts.com/profile', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(6000);
out.url1 = page.url();
const t1 = await page.evaluate(() => document.body.innerText);
out.hasProfile = /profile|аккаунт|API token/i.test(t1);

// 点击 "API token" 标签（只点 tab 文本，不碰 Update token 按钮）
try {
  const tab = page.getByText(/api\s*token/i, { exact: false }).first();
  if (await tab.count()) {
    await tab.click({ timeout: 5000 });
    await page.waitForTimeout(3000);
  } else {
    out.note = '未见 API token 标签文本';
  }
} catch (e) { out.clickErr = String(e).slice(0, 100); }

out.url2 = page.url();
const t2 = await page.evaluate(() => document.body.innerText);
out.tokens = [...new Set(t2.match(/\b[a-f0-9]{32,40}\b/g) || [])];
out.text2 = t2.slice(0, 1200);

fs.writeFileSync(
  'D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/_research/tabbit/tp_token.txt',
  JSON.stringify({ url: out.url2, tokens: out.tokens, at: new Date().toISOString() }, null, 2)
);
return out;
