// tp7.js — 提取支持文章内的全部指导截图
const out = { imgs: [] };
await page.goto('https://support.travelpayouts.com/hc/en-us/articles/13024069738386-Where-to-find-API-token',
  { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(4000);
const metas = await page.evaluate(() =>
  Array.from(document.querySelectorAll('article img, .article-body img, .article__body img'))
    .map(i => ({ src: (i.currentSrc || i.src || '').slice(0, 120), w: i.naturalWidth, h: i.naturalHeight }))
    .filter(x => x.w >= 200)   // 过滤图标
);
out.imgs = metas;
let i = 0;
for (const im of await page.$$('article img, .article-body img, .article__body img')) {
  const box = await im.boundingBox();
  if (!box || box.width < 200) continue;
  try {
    await im.scrollIntoViewIfNeeded();
    const path = `D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/_research/tabbit/tp_img_${i}.png`;
    await im.screenshot({ path });
    out.imgs[i] = out.imgs[i] || {};
    out.imgs[i].file = path;
  } catch (e) { out.imgs[i] = out.imgs[i] || {}; out.imgs[i].err = String(e).slice(0, 80); }
  i++;
}
return out;
