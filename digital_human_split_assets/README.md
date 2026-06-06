# 数字人形象分层资源包

已拆出以下素材：

- `base_halfbody.png`：基础半身图
- `mouth_closed.png`、`mouth_small.png`、`mouth_mid.png`、`mouth_big.png`、`mouth_round.png`：5 张嘴型图
- `expr_smile.png`、`expr_enthusiastic.png`、`expr_thinking.png`：3 张表情图
- `blink_open.png`、`blink_closed.png`：2 张眨眼图
- `config.json`：小程序层叠定位配置
- `asset_sheet_source.png`：原始角色资产板，便于后续美术继续精修

## 推荐小程序层级

基础口型同步页面建议这样叠：

1. `base_halfbody.png`
2. `mouth_xxx.png`，放到 `config.json` 的 `mouthBox`
3. 眨眼瞬间显示 `blink_closed.png`，放到 `config.json` 的 `blinkBox`

3 张 `expr_*.png` 是完整表情状态图，更适合在“欢迎 / 热情讲解 / 思考”状态时直接替换基础图，而不是当透明 overlay 使用。

## 说明

这是开发可用版素材。由于当前来源是单张生成图/资产板，不是 PSD 或 Live2D 源文件，所以嘴型、眨眼层采用了局部裁切 + 透明蒙版的方式；可以直接用于 MVP 联调，最终参赛版建议让美术再按这个结构精修分层。
