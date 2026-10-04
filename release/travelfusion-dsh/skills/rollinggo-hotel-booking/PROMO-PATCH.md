# PROMO-PATCH.md — 推广归因补丁（<YOUR_PROMO_CODE>）

本技能是 **分发版**：在官方 rollinggo-hotel-skill-CN 之上打了推广归因补丁。
技能更新（`npx skills add` / `git pull`）会覆盖回官方原版——**更新后必须重新打补丁**。

## 补丁内容（共 3 处）

### 1. `scripts/rgh.js` — 代码级强制（核心）
- `spawn` 的 stdout 由 `inherit` 改为 `pipe`，逐行经过 `applyPromo()` 转发
- `applyPromo()`：`utm_source=rollinggo_cus` → `utm_source=<YOUR_PROMO_CODE>`（换值）；
  rollinggo.cn 链接若无 `utm_source` 则追加 `&utm_source=<YOUR_PROMO_CODE>`
- 逐行流式处理，login 等交互命令不受影响；stderr 与退出码原样透传
- 搜索标记：源码内 `PROMO PATCH (<YOUR_PROMO_CODE>)` 注释块

### 2. `SKILL.md` — 规则层兜底
- 输出规范第 6 条 + 「推广归因（强制后处理）」节
- 覆盖 Agent 自己拼链接（不经 CLI）的场景

### 3. `trip-planner/SKILL.md` 2d — 宿主编排层同款规则

## 更新后重打补丁

1. 官方新版覆盖后，把上面第 1 条的 PROMO PATCH 块重新合入新 `rgh.js`（或在 git 里维护本目录）
2. 核对 SKILL.md 输出规范第 6 条仍在
3. 验证：`node scripts/rgh.js search-hotels --place 杭州 --place-type 城市 --size 1`
   → 输出中 bookingUrl 必须带 `utm_source=<YOUR_PROMO_CODE>`

## 佣金机制备忘

- 归因跟**链接**走：经本技能产出的分享链接全部带码 → 计佣
- 别人从官方仓库自己装原版 → 链接不带码 → 不计佣；要保佣金就分发本目录副本
