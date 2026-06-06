# 景区导览服务 AI 数字人

本仓库包含景区导览后台、游客端小程序、路线推荐/步行导览、AI 问答、语音合成与 DH_live 数字人样片。

## 项目结构

```text
backend/                    FastAPI 后端服务
admin-web/                  Vue 3 后台管理端
miniprogram/                uni-app 微信小程序端
prototypes/dh-live-guide/   DH_live H5 数字人样片
data/                       景区资料与导入样例
docs/                       设计文档、实施计划、启动说明
uploads/                    本地上传目录，仅保留 .gitkeep
```

## 环境要求

- Python 3.11+
- Node.js 18+
- npm 9+
- MySQL 5.7 或 8.0
- 微信开发者工具

Windows PowerShell 下建议使用 `npm.cmd`，避免脚本执行策略问题。

## 1. 克隆代码

```powershell
git clone https://github.com/Darkerlf/AI-digital-person.git
cd AI-digital-person
```

如果需要指定当前默认开发分支：

```powershell
git checkout feature/admin-backend-phase1
```

## 2. 后端配置与启动

创建数据库：

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS scenic_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

创建虚拟环境并安装依赖：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

创建本地环境变量文件：

```powershell
Copy-Item .env.example .env
notepad .env
```

至少需要按本机情况修改：

```env
DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/scenic_admin
JWT_SECRET_KEY=请换成随机字符串
DASHSCOPE_API_KEY=你的阿里云 DashScope Key
TENCENT_MAP_KEY=你的腾讯位置服务 Key
```

初始化数据库和默认管理员：

```powershell
.\.venv\Scripts\python init_db.py
```

启动后端：

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

验证：

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing
```

接口文档地址：

```text
http://127.0.0.1:8000/docs
```

默认后台账号：

```text
admin / admin123
```

## 3. 后台管理端启动

打开新终端：

```powershell
cd admin-web
npm.cmd install
npm.cmd run dev
```

浏览器访问终端输出的地址，通常是：

```text
http://localhost:5173
```

后台 API 默认访问：

```text
http://127.0.0.1:8000/api
```

## 4. 微信小程序端启动

打开新终端：

```powershell
cd miniprogram
npm.cmd install
Copy-Item .env.example .env.local
```

微信开发者工具模拟器联调时，`.env.local` 可保持：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_DH_LIVE_GUIDE_URL=http://localhost:58120/runtime/index.html
```

构建微信小程序包：

```powershell
npm.cmd run build:mp-weixin
```

用微信开发者工具导入：

```text
miniprogram/dist/build/mp-weixin
```

不要直接导入 `miniprogram` 源码目录。

真机联调时，不能使用 `127.0.0.1`。请把 `.env.local` 的 `VITE_API_BASE_URL` 改成电脑局域网 IP，例如：

```env
VITE_API_BASE_URL=http://192.168.1.20:8000/api
```

并确保后端启动参数包含 `--host 0.0.0.0`，手机和电脑处于同一局域网。

## 5. DH_live 数字人样片

小程序中的 DH_live 页面默认打开：

```text
http://localhost:58120/runtime/index.html
```

本地启动样片静态服务：

```powershell
cd prototypes/dh-live-guide
python -m http.server 58120 --bind 0.0.0.0
```

浏览器访问：

```text
http://localhost:58120/runtime/index.html
```

说明：`prototypes/dh-live-guide/runtime/` 默认不纳入 Git，因为其中可能包含上游 Web Demo 文件、演示角色素材和授权受限资源。首次运行前，请按 `prototypes/dh-live-guide/README.md` 的说明执行 `scripts/stage-dh-live-runtime.ps1`，或把已授权的 runtime 文件放入该目录。

原始 DH_live 训练权重体积较大，不纳入普通 Git 提交。

## 6. 测试与构建

后端测试：

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests -q
```

后台管理端：

```powershell
cd admin-web
npm.cmd run test
npm.cmd run build
```

小程序结构测试与构建：

```powershell
cd miniprogram
Get-ChildItem tests -Filter *.mjs | ForEach-Object { node $_.FullName }
npm.cmd run build:mp-weixin
```

DH_live 样片测试：

```powershell
cd prototypes/dh-live-guide
npm.cmd test
```

## 7. 配置与安全

不要提交真实密钥、密码、`.env`、`.env.local`、数据库文件、日志或本地上传文件。仓库只提供 `.env.example` 模板。

常用密钥来源：

- `DASHSCOPE_API_KEY`：阿里云 DashScope，用于 AI 问答和语音能力
- `TENCENT_MAP_KEY`：腾讯位置服务，用于坐标解析和步行路线规划
- `ALIYUN_OSS_ACCESS_KEY_ID` / `ALIYUN_OSS_ACCESS_KEY_SECRET`：游客头像 OSS 上传

个人小程序无法配置 `web-view` 业务域名时，DH_live H5 页面只能作为开发样片；上线版本建议使用小程序原生数字人组件。

更多本地启动细节见：

```text
docs/start-frontend-backend.md
```
