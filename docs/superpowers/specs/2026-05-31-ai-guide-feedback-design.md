# AI 导游沉浸页与回答评价设计

## 目标

严格参考游客端设计稿重构 DH_live AI 导游页，并让游客可以对每条 AI 回答点赞、点踩或提交 1-5 星详细评论。所有反馈必须绑定到真实回答，并在后台管理端可查看。

## 页面结构

- 小程序继续使用原生顶部导航，不在 WebView 内重复绘制标题栏。
- 数字人舞台位于页面上半部，状态胶囊固定在舞台右上角。
- 舞台左下角提供音量按钮，右下角提供全屏按钮。
- 白色讲解面板覆盖舞台底部，包含朱砂色说明、主标题、快捷问题、回答气泡和底部输入栏。
- 每条 AI 回答下方显示 `赞`、`踩`、`详细评论`。
- 详细评论使用当前页底部半屏面板，支持 1-5 星和文字评论。

## 数据链路

- 流式问答结束后，后端返回 `session_id` 和 `message_id`。
- DH_live 页面保存当前回答的 `message_id`。
- 游客提交反馈时调用 `/api/tourist/feedback`，将 `message_id` 写入 `feedback_record.source_id`。
- 后端同步更新 `conversation_message.feedback_status`。
- 后台 `/api/dashboard/feedback-report` 返回汇总数据和最新评价明细。
- 后台“游客感受度报告”展示点赞、点踩、星级、评论、问题和 AI 回答摘要。

## 兼容性

- 不新增数据库列，复用现有 `feedback_record.source_type/source_id/score/content`。
- 保留现有 DH_live 音频播放、动态数字人和小程序 WebView 入口。
- 不改小程序 tabBar 和页面路径。

