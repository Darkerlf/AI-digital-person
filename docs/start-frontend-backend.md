# 前后端与小程序启动命令

本文档用于在本机启动 FastAPI 后端、后台管理端、微信小程序前端，以及 DH_live 高拟真数字人样片。

项目根目录：

```text
D:\AI digital person\.worktrees\admin-backend-phase1
```

Python 解释器：

```text
D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe
```

## 1. 启动后端

先确认 `backend\.env` 或系统环境变量中已经配置：

```text
DASHSCOPE_API_KEY
```

启动 FastAPI：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
& "D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

健康检查：

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing
```

正常返回：

```json
{"status":"ok"}
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 2. 启动后台管理端

首次启动或依赖缺失时，先安装依赖：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\admin-web"
npm.cmd install
```

启动开发服务：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\admin-web"
npm.cmd run dev -- --host 0.0.0.0 --port 5173
```

浏览器访问：

```text
http://localhost:5173
```

如果 `5173` 端口被占用，可以改用其他端口：

```powershell
npm.cmd run dev -- --host 0.0.0.0 --port 5174
```

## 3. 启动微信小程序开发构建

首次启动或依赖缺失时，先安装依赖：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
npm.cmd install
```

微信开发者工具联调时，使用本机回环地址：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

真机联调前，先查询电脑当前局域网 IPv4 地址：

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike "127.*" -and $_.PrefixOrigin -ne "WellKnown" } |
  Select-Object InterfaceAlias,IPAddress
```

如果局域网地址发生变化，复制环境变量模板并修改其中的 IP：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
Copy-Item .env.example .env.local
notepad .env.local
```

真机联调地址示例：

```text
VITE_API_BASE_URL=http://172.27.35.118:8000/api
```

`VITE_API_BASE_URL` 可以在真机联调时使用电脑局域网地址。`VITE_DH_LIVE_GUIDE_URL` 的规则不同：

- 微信开发者工具中默认使用 `http://localhost:58120/runtime/index.html`
- 真机 `web-view` 必须使用已在微信公众平台配置的 HTTPS 业务域名，例如：

```text
VITE_DH_LIVE_GUIDE_URL=https://guide.example.com/runtime/index.html
```

启动微信小程序开发构建：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
npm.cmd run dev:mp-weixin
```

启动成功后，用微信开发者工具导入：

```text
D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram\dist\dev\mp-weixin
```

注意：不要直接导入 `miniprogram` 源码目录，应该导入 `dist\dev\mp-weixin`。

## 4. 微信小程序发布构建

需要上传发布包时运行：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
npm.cmd run build:mp-weixin
```

构建完成后，用微信开发者工具导入或上传：

```text
D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram\dist\build\mp-weixin
```

## 5. 启动 DH_live 高拟真数字人样片

小程序的“高拟真数字人”页面默认通过 `web-view` 打开：

```text
http://localhost:58120/runtime/index.html
```

本地启动样片静态服务：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\prototypes\dh-live-guide"
& "D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m http.server 58120 --bind 0.0.0.0
```

浏览器访问：

```text
http://localhost:58120/runtime/index.html
```

如果微信开发者工具缓存了旧页面，可以加一个查询参数强制刷新：

```text
http://localhost:58120/runtime/index.html?refresh=1
```

## 6. 常用测试命令

后端语音相关测试：

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
& "D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m pytest tests/test_tts_service.py tests/test_tourist_voice_api.py -q
```

测试对话接口：

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/tourist/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message":"你好","scenic_area_id":1}' `
  -UseBasicParsing
```

测试语音和口型同步接口：

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/tourist/voice/tts-sync" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"欢迎来到灵山胜境","voice":"loongbella_v3"}' `
  -UseBasicParsing
```

测试 DH_live 用的 WAV 语音接口：

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/tourist/voice/avatar-tts" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"欢迎来到灵山胜境","voice":"loongbella_v3"}' `
  -OutFile "$env:TEMP\avatar-tts.wav"
```

## 7. 停止服务

停止后端时，先查找 `8000` 端口进程：

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
  Select-Object LocalAddress,LocalPort,State,OwningProcess
```

停止对应进程：

```powershell
Stop-Process -Id <OwningProcess> -Force
```

后台管理端、小程序开发构建、DH_live 静态服务通常在对应终端窗口按 `Ctrl + C` 停止。

## 8. 微信开发者工具注意事项

本地联调时，如果请求被拦截，可以在微信开发者工具中检查：

- 点击“详情”
- 勾选“不校验合法域名、web-view、TLS 版本以及 HTTPS 证书”
- 点击“清缓存 -> 清除全部缓存”
- 重新“编译”

小程序真机联调时只使用 `VITE_API_BASE_URL` 指定的后端地址。不要配置 `localhost` 或 `127.0.0.1`，因为它们在手机上指向手机自身。

```text
http://172.27.35.118:8000/api
```

如果本机 IP 变化，需要同步修改：

```text
miniprogram\.env.local
```

真机需要与电脑连接同一个局域网，并确保后端使用 `--host 0.0.0.0`。DH_live 静态服务使用 `--bind 0.0.0.0` 后可以通过手机浏览器核验本地页面，但小程序真机中的 `web-view` 仍应使用 HTTPS 业务域名。

正式发布时不能继续使用局域网 IP 和 HTTP。需要把 API 部署为 HTTPS，并在微信公众平台配置 `request` 合法域名；DH_live 页面还需要部署为 HTTPS，并配置业务域名。

## 9. API Key 配置说明

后端会读取：

```text
DASHSCOPE_API_KEY
```

如果同时存在系统环境变量和 `backend\.env`，以当前进程实际读取到的配置为准。修改 API Key 后不需要重启电脑，但需要重启后端进程。

不要把真实 API Key 写进文档、代码或提交到 Git。

## 10. 游客头像 OSS 配置

游客选择微信头像后，小程序会先上传到后端，再由后端写入 OSS。后端环境变量需要配置：

```text
ALIYUN_OSS_ACCESS_KEY_ID
ALIYUN_OSS_ACCESS_KEY_SECRET
ALIYUN_OSS_BUCKET=digital-person-ai
ALIYUN_OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

Bucket 使用公共读时，游客头像会返回稳定的 HTTPS URL。正式发布前，在微信公众平台配置：

```text
downloadFile 合法域名：https://digital-person-ai.oss-cn-beijing.aliyuncs.com
uploadFile 合法域名：后端 API 的 HTTPS 域名
request 合法域名：后端 API 的 HTTPS 域名
```

微信开发者工具本地联调时可以继续勾选“不校验合法域名、web-view、TLS 版本以及 HTTPS 证书”。
