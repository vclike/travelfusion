// tp1.js — Travelpayouts 控制台侦察：登录态 + API/token 入口枚举
const out = { steps: [] };
await page.goto('https://travelpayouts.com/dashboard', { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(6000);
out.url = page.url();
out.title = await page.title();
out.loginCookies = (await context.cookies())
  .map(c => c.name)
  .filter(n => /session|auth|token|user|login/i.test(n))
  .slice(0, 12);
// 登录墙判定：页面上有没有密码框
out.hasPasswordField = await page.evaluate(() => !!document.querySelector('input[type="password"]'));
// 枚举疑似入口
out.entries = await page.evaluate(() =>
  Array.from(document.querySelectorAll('a,button,[role="menuitem"]'))
    .map(a => ({ t: ((a.textContent || '').trim() || '').slice(0, 60), h: (a.href || '') }))
    .filter(x => /api|token|маркер|настройк|settings|аккаунт|account|профил|profile|key/i.test(x.t + ' ' + x.h))
    .slice(0, 40)
);
return out;
