# 游客头像 OSS 持久化设计

## 目标

修复微信小程序 `chooseAvatar` 返回临时文件后被直接写入游客资料的问题。游客头像必须上传到阿里云 OSS，并以稳定 HTTPS URL 保存到 MySQL。OSS 不可用时阻止保存，不回退到后端本地文件或微信临时路径。

## 数据流

1. 游客在“我的”页面选择头像，小程序仅使用临时路径进行本地预览。
2. 游客点击“保存资料”。
3. 如果头像为新选择的本地临时文件，小程序使用 `uni.uploadFile` 上传至 `POST /api/tourist/profile/avatar`。
4. 后端通过游客 Bearer token 鉴权，校验文件类型和大小，将文件上传到 OSS 的 `visitor-avatars` 前缀。
5. 后端更新游客 `avatar_url`，返回 OSS 公共读 HTTPS URL。
6. 小程序使用返回的稳定 URL 再调用现有 `PUT /api/tourist/profile` 保存昵称，并将稳定 URL写入本地缓存。

## 接口

`POST /api/tourist/profile/avatar`

- 鉴权：`Authorization: Bearer <visitor-token>`
- 请求：multipart form-data，字段名 `avatar`
- 允许类型：`image/jpeg`、`image/png`、`image/webp`
- 大小限制：2 MiB
- 成功响应：

```json
{
  "visitor_id": 1,
  "nickname": "游客昵称",
  "avatar_url": "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/scenic-guide/visitor-avatars/2026/06/01/<uuid>-avatar.jpeg"
}
```

## 错误处理

- 缺少文件、类型不支持、文件超过 2 MiB：返回 `400`。
- OSS 未配置或 OSS 上传失败：返回 `503`。
- 小程序收到上传失败后保留当前预览和昵称输入，提示用户稍后重试，不调用资料保存接口。
- 小程序不得将 `wxfile://`、`http://tmp/`、开发者工具 `__tmp__` 路径写入后端资料。

## 历史数据修复

增加脚本清空数据库中已存在的临时头像 URL。脚本只匹配 `wxfile://`、`http://tmp/`、`https://tmp/` 和包含 `/__tmp__/` 的地址，不影响真实远程头像。

## 测试

- 后端 API 测试覆盖 OSS 上传成功、非法类型、超大文件、OSS 不可用和鉴权。
- 小程序契约测试覆盖 `uni.uploadFile`、`/tourist/profile/avatar`、Bearer token、临时头像先上传再保存。
- 运行后端测试、小程序脚本检查和 `npm.cmd run build:mp-weixin`。
