// tp8.js — 全页截图 + 全量 img 枚举
const out = {};
await page.goto('https://support.travelpayouts.com/hc/en-us/articles/13024069738386-Where-to-find-API-token',
  { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
await page.waitForTimeout(5000);
out.allImgs = await page.evaluate(() =>
  Array.from(document.images).map(i => ({
    src: (i.currentSrc || i.src || '').slice(0, 110),
    w: i.naturalWidth, h: i.naturalHeight, vis: !!i.offsetParent
  }))
);
await page.screenshot({ path: 'D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/_research/tabbit/tp_article_full.png', fullPage: true });
out.shot = 'tp_article_full.png';
return out;
