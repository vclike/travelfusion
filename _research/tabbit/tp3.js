// tp3.js — 读官方支持文章：Where to find API token
const out = {};
await page.goto('https://support.travelpayouts.com/hc/en-us/articles/13024069738386-Where-to-find-API-token',
  { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(4000);
out.url = page.url();
out.title = await page.title();
// Zendesk 文章正文
out.body = await page.evaluate(() => {
  const art = document.querySelector('article') || document.querySelector('.article-body') || document.body;
  return (art.innerText || '').replace(/\n{3,}/g, '\n\n').slice(0, 3500);
});
// 顺带抓正文里的内部链接（可能直达 token 页）
out.links = await page.evaluate(() =>
  Array.from(document.querySelectorAll('article a, .article-body a'))
    .map(a => ({ t: (a.textContent || '').trim().slice(0, 60), h: a.href }))
    .filter(x => /token|dashboard|account|api/i.test(x.t + x.h))
    .slice(0, 20)
);
return out;
