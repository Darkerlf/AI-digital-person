# 微信小程序数字人口型同步部署说明

## 本地联调

1. 后端配置 `.env`：

```env
DASHSCOPE_API_KEY=你的阿里云DashScope Key
TTS_MODEL=qwen3-tts-instruct-flash
TTS_VOICE=Chelsie
TTS_RESPONSE_FORMAT=mp3
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

2. 启动 FastAPI：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. 确认电脑局域网 IP，并把 `miniprogram/src/api/request.ts` 的小程序端 `API_BASE_URL` 改成：

```ts
export const API_BASE_URL = 'http://你的局域网IP:8000/api'
```

4. 启动微信小程序构建：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
npm.cmd run dev:mp-weixin
```

5. 用微信开发者工具打开 `miniprogram/dist/dev/mp-weixin`。

## 线上发布

1. 后端部署到 HTTPS 域名，例如 `https://api.example.com`。
2. 在微信公众平台的小程序后台配置合法域名：
   - `request合法域名`: `https://api.example.com`
   - `downloadFile合法域名`: `https://api.example.com`
3. 将 `miniprogram/src/api/request.ts` 的小程序端 `API_BASE_URL` 改成：

```ts
export const API_BASE_URL = 'https://api.example.com/api'
```

4. 构建发布包：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
npm.cmd run build:mp-weixin
```

5. 用微信开发者工具打开 `miniprogram/dist/build/mp-weixin` 上传。

## 安全

- 不要把真实 API key 写入代码、文档、`.env.example` 或小程序文件。
- 当前聊天里暴露过的阿里云 API key 建议立即在阿里云控制台轮换。
- 小程序端只能访问你的业务后端，不能直接访问 DashScope。
