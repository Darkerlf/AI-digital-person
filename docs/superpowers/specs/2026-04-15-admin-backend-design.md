# 景区导览服务 AI 数字人后台首期设计规格

## 1. 目标与范围

### 1.1 首期目标

基于现有需求文档与景区资料，建设一个可用的管理后台首期版本，优先打通以下业务闭环：

- 管理员登录进入后台
- 导入真实景区结构化数据、知识文档和行为分析 Excel
- 在后台完成景区、景点、知识文档、FAQ、数字人配置的管理
- 基于真实导入数据生成后台统计与运营大屏
- 为后续 AI 问答、RAG、ASR、TTS 能力预留标准接口与配置位

### 1.2 首期明确包含

- 后台前端：`Vue 3 + Element Plus`
- 后台后端：`FastAPI`
- 数据库：`MySQL`
- 文件存储：本地 `uploads/`
- 数据导入：
  - 结构化景点数据导入
  - Word/Markdown/TXT 文档导入
  - Excel 行为数据导入
- 业务管理：
  - 景区管理
  - 景点管理
  - 知识文档管理
  - FAQ 管理
  - 数字人配置
  - AI 配置预留
  - 操作日志
- 统计分析：
  - 工作台概览
  - 数据大屏
  - 热门景点/行为趋势统计

### 1.3 首期明确不包含

- 游客端小程序
- 实际 RAG 检索与问答链路
- ASR / TTS / 数字人驱动的真实模型调用
- 向量化、重排和召回服务
- 微服务拆分、消息队列、对象存储等重型基础设施

## 2. 总体架构

采用“模块化单体”架构，以较低实现成本完成真实后台闭环，同时为后续扩展保留清晰边界。

### 2.1 系统组成

- `admin-web`
  - Vue 3 管理后台
  - 提供登录、数据管理、导入、统计、配置页面
- `admin-api`
  - FastAPI 后端服务
  - 提供鉴权、CRUD、导入、统计、日志与配置接口
- `mysql`
  - 存储业务数据、导入任务、统计结果、配置数据
- `uploads/`
  - 存储导入原始文件和后续附件资源
- `ai_adapter`
  - 提供未来 AI 服务接入的统一配置与调用入口

### 2.2 架构原则

- 首期坚持单体部署，避免过早拆分
- 业务模块内聚，接口按资源边界划分
- 导入流程统一通过任务模型管理
- 统计查询依赖汇总表，不直接扫原始明细
- AI 能力先预留适配层，不让业务代码依赖具体厂商

## 3. 数据模型

### 3.1 鉴权与审计

#### `admin_user`

- `id`
- `username`
- `password_hash`
- `role`
- `status`
- `last_login_at`
- `created_at`
- `updated_at`

角色首期使用枚举：

- `super_admin`
- `content_admin`
- `ops_admin`

#### `operation_log`

- `id`
- `admin_user_id`
- `module`
- `action`
- `target_type`
- `target_id`
- `detail_json`
- `created_at`

### 3.2 景区与景点主数据

#### `scenic_area`

- `id`
- `code`
- `name`
- `description`
- `status`
- `created_at`
- `updated_at`

#### `scenic_spot`

- `id`
- `scenic_area_id`
- `spot_code`
- `name`
- `alias`
- `location_text`
- `latitude`
- `longitude`
- `parameters_text`
- `core_function`
- `cultural_value`
- `detail_intro`
- `highlights`
- `performance_info`
- `remarks`
- `suggested_duration_minutes`
- `open_status`
- `created_at`
- `updated_at`

#### `scenic_spot_tag`

- `id`
- `scenic_spot_id`
- `tag_name`

### 3.3 知识管理

#### `knowledge_document`

- `id`
- `scenic_area_id`
- `title`
- `doc_type`
- `source_path`
- `source_name`
- `content_text`
- `status`
- `version`
- `imported_at`
- `created_by`
- `updated_at`

#### `knowledge_chunk`

- `id`
- `document_id`
- `chunk_index`
- `chunk_text`
- `token_count`
- `source_section`
- `status`
- `created_at`

#### `faq_item`

- `id`
- `scenic_area_id`
- `question`
- `answer`
- `category`
- `priority`
- `status`
- `source`
- `created_at`
- `updated_at`

### 3.4 导入任务

#### `import_job`

- `id`
- `job_type`
- `source_file_name`
- `source_file_path`
- `status`
- `total_count`
- `success_count`
- `failed_count`
- `error_message`
- `started_at`
- `finished_at`
- `created_by`

#### `import_job_item`

- `id`
- `import_job_id`
- `item_type`
- `raw_payload_json`
- `target_type`
- `target_id`
- `status`
- `error_message`

### 3.5 统计与分析

#### `visitor_behavior_event`

- `id`
- `scenic_area_id`
- `event_time`
- `visitor_id`
- `session_id`
- `event_type`
- `event_value`
- `spot_name`
- `route_name`
- `raw_json`
- `created_at`

#### `dashboard_stat_daily`

- `id`
- `stat_date`
- `scenic_area_id`
- `total_visitors`
- `total_events`
- `hot_spot_top_json`
- `hot_question_top_json`
- `route_usage_json`
- `satisfaction_score`
- `created_at`

#### `feedback_record`

- `id`
- `scenic_area_id`
- `source_type`
- `source_id`
- `sentiment`
- `score`
- `content`
- `created_at`

### 3.6 数字人与 AI 预留

#### `digital_human_config`

- `id`
- `scenic_area_id`
- `name`
- `avatar_url`
- `voice_style`
- `welcome_text`
- `default_mode`
- `config_json`
- `status`
- `created_at`
- `updated_at`

#### `ai_provider_config`

- `id`
- `provider_name`
- `model_type`
- `endpoint`
- `api_key_masked`
- `extra_config_json`
- `status`
- `created_at`
- `updated_at`

## 4. 后台信息架构

### 4.1 一级导航

- 登录页
- 工作台
- 景区与景点管理
- 知识管理
- 数据导入
- 数据大屏
- 数字人配置
- 系统设置

### 4.2 页面清单

#### 工作台

- 核心概览卡片
- 最近导入任务
- 快捷入口

#### 景区与景点管理

- 景区管理
- 景点列表
- 景点详情/编辑

#### 知识管理

- 知识文档列表
- 文档详情与切片预览
- FAQ 管理

#### 数据导入

- 导入中心
- 导入任务记录
- 导入明细

#### 数据大屏

- 运营概览
- 热门景点分析
- 行为趋势统计

#### 数字人配置

- 配置列表
- 配置编辑

#### 系统设置

- 管理员账号
- AI 接口配置
- 操作日志

### 4.3 推荐路由

- `/login`
- `/dashboard`
- `/scenic-areas`
- `/scenic-spots`
- `/scenic-spots/:id`
- `/knowledge/documents`
- `/knowledge/documents/:id`
- `/knowledge/faqs`
- `/imports`
- `/imports/:id`
- `/analytics/dashboard`
- `/digital-humans`
- `/settings/admin-users`
- `/settings/ai-providers`
- `/settings/operation-logs`

## 5. 后端模块划分

### 5.1 建议目录

```text
backend/
  app/
    main.py
    core/
    models/
    schemas/
    api/
      deps.py
      routers/
    services/
    repositories/
    importers/
      parsers/
    tasks/
    utils/
  tests/
```

### 5.2 模块职责

- `auth`
  - 登录、JWT、当前用户
- `scenic_areas`
  - 景区 CRUD
- `scenic_spots`
  - 景点 CRUD、搜索、标签
- `knowledge`
  - 文档管理、切片预览、FAQ
- `imports`
  - 三类导入与任务记录
- `dashboard`
  - 工作台概览与统计查询
- `digital_humans`
  - 数字人配置管理
- `settings`
  - 管理员与 AI 配置
- `operation_logs`
  - 审计查询

### 5.3 分层边界

- `api/routers`
  - 处理 HTTP 层逻辑
- `services`
  - 编排业务流程
- `repositories`
  - 数据库访问
- `importers`
  - 文件解析与数据映射
- `tasks`
  - 切片与统计汇总
- `ai_adapter_service`
  - 未来 AI 提供方适配入口

## 6. 接口边界

### 6.1 鉴权

- `POST /api/auth/login`
- `GET /api/auth/me`

### 6.2 景区

- `GET /api/scenic-areas`
- `POST /api/scenic-areas`
- `PUT /api/scenic-areas/{id}`
- `DELETE /api/scenic-areas/{id}`

### 6.3 景点

- `GET /api/scenic-spots`
- `GET /api/scenic-spots/{id}`
- `POST /api/scenic-spots`
- `PUT /api/scenic-spots/{id}`
- `DELETE /api/scenic-spots/{id}`

### 6.4 知识文档与 FAQ

- `GET /api/knowledge/documents`
- `POST /api/knowledge/documents/upload`
- `GET /api/knowledge/documents/{id}`
- `GET /api/knowledge/documents/{id}/chunks`
- `PUT /api/knowledge/documents/{id}`
- `GET /api/knowledge/faqs`
- `POST /api/knowledge/faqs`
- `PUT /api/knowledge/faqs/{id}`
- `DELETE /api/knowledge/faqs/{id}`

### 6.5 导入任务

- `POST /api/imports/scenic-spots`
- `POST /api/imports/knowledge-docs`
- `POST /api/imports/behavior-events`
- `GET /api/imports/jobs`
- `GET /api/imports/jobs/{id}`
- `GET /api/imports/jobs/{id}/items`

### 6.6 数据大屏

- `GET /api/dashboard/overview`
- `GET /api/dashboard/hot-spots`
- `GET /api/dashboard/behavior-trends`

### 6.7 数字人配置

- `GET /api/digital-humans`
- `POST /api/digital-humans`
- `PUT /api/digital-humans/{id}`

### 6.8 系统设置

- `GET /api/settings/ai-providers`
- `POST /api/settings/ai-providers`
- `PUT /api/settings/ai-providers/{id}`
- `GET /api/settings/admin-users`
- `POST /api/settings/admin-users`

### 6.9 操作日志

- `GET /api/operation-logs`

## 7. 导入设计

### 7.1 统一流程

所有导入统一遵循以下步骤：

1. 上传原始文件到 `uploads/`
2. 创建 `import_job`
3. 根据导入类型调用对应 importer
4. 逐条处理并写入 `import_job_item`
5. 成功数据落业务表
6. 更新任务状态
7. 视情况触发切片或统计汇总

### 7.2 结构化景点导入

来源：`景点结构化数据集.docx`

规则：

- 解析 Word 表格
- 关键字段必填：
  - 景区名称
  - 景点 ID
  - 景点名称
- 使用 `spot_code` 作为幂等更新键
- 景区不存在时自动创建
- 单条失败不影响整批任务

### 7.3 知识文档导入

来源：`.docx / .md / .txt`

规则：

- 按后缀选择 parser
- 提取正文并清洗空白噪音
- 写入 `knowledge_document`
- 自动生成 `knowledge_chunk`
- 同景区同文件允许形成版本记录

### 7.4 行为数据导入

来源：`xlsx`

规则：

- 支持列名映射
- 逐行落入 `visitor_behavior_event`
- 原始行保存到 `raw_json`
- 导入后重算受影响日期的统计数据
- 支持部分成功

## 8. 切片策略

首期切片只服务于知识管理和未来 RAG 预留，不做向量化。

策略：

- 先按自然段分割
- 再按长度聚合到约 `300-800` 中文字符
- 过滤空白、纯标点、极短段
- 保留章节或段落位置信息

切片结果至少包含：

- `chunk_index`
- `chunk_text`
- `token_count`
- `source_section`

## 9. 统计设计

### 9.1 统计分层

- 原始层：`visitor_behavior_event`
- 汇总层：`dashboard_stat_daily`

### 9.2 汇总时机

- Excel 导入完成后重算受影响日期
- 首期允许同步执行
- 后续可替换为定时任务或异步任务

### 9.3 首期统计项

- 总事件量
- 按景区统计事件量
- 热门景点 Top N
- 行为趋势按天统计
- 路线使用 Top N
- 满意度字段保留但不伪造数据

## 10. 错误处理

### 10.1 导入失败分层

- 文件级失败
  - 文件损坏
  - 格式不支持
  - 表格不存在
- 记录级失败
  - 字段缺失
  - 时间格式错误
  - 必填项为空
- 后置处理失败
  - 文档保存成功但切片失败
  - 行为数据落表成功但统计失败

### 10.2 错误展示原则

- 后台页面显示可读错误文案
- 服务端日志记录详细异常
- 单条失败不影响整批导入

### 10.3 统一状态

以下状态在导入任务与相关页面统一使用：

- `pending`
- `processing`
- `success`
- `partial_success`
- `failed`

## 11. AI 预留设计

首期不接 AI 模型，但预留统一适配层：

- `list_provider_configs()`
- `get_active_provider(model_type)`
- `build_future_client_config()`

后续接入 RAG、ASR、TTS 时，仅扩展适配层与独立服务，不直接改动景点、知识、统计主业务。

## 12. 首期交付标准

首期完成后，应至少达到以下结果：

- 可通过管理员账号登录后台
- 可管理景区与景点数据
- 可导入真实结构化景点数据
- 可导入知识文档并预览切片
- 可导入行为分析 Excel 并生成统计结果
- 可查看工作台与数据大屏的真实统计
- 可配置数字人基础信息与 AI 接口预留参数
- 关键操作有审计日志

## 13. 风险与约束

### 13.1 风险

- `.docx` 结构可能不规整，影响解析稳定性
- Excel 字段可能与预期不完全一致，需要容错映射
- 行为数据语义未完全固定，首期统计口径需保持保守
- 当前仓库不是 git 仓库，无法按常规流程提交设计文档版本

### 13.2 约束

- 首期优先真实可用，不追求大而全
- 不引入微服务或异步任务基础设施
- 不将 AI 集成作为首期阻塞项
- 所有统计必须建立在真实导入数据基础上
