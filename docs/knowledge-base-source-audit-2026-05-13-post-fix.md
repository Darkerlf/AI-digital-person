# 知识库修复后复核

复核时间：2026-05-13

源目录：`D:\AI digital person\.worktrees\admin-backend-phase1\data`

## 当前结果

| 项目 | 数量 |
| --- | ---: |
| knowledge_document | 3 |
| knowledge_chunk | 80 |
| 已生成 embedding 的 chunk | 80 |
| scenic_spot | 22 |
| 错误表头景点记录 | 0 |
| visitor_behavior_event | 140447 |

## 源文档匹配情况

| 源文件 | 当前状态 |
| --- | --- |
| 灵山胜境 景点结构化数据集.docx | 已按段落 + 表格完整导入知识库 |
| 灵山胜境：历史、文化、景点特色与个性化游览指南.docx | 已按段落 + 表格完整导入知识库 |
| 景点景区旅游数据行为分析数据.xlsx | 已生成聚合知识文档，并导入行为事件表 |

## 问答检索验证

`门票多少钱` 的当前首条检索结果命中票务切片：

`成人票 | 210元 | 18周岁以上成年人 ... 半价票 | 105元 ... 免票 | 0元 ... 网购联票 | 225元 ...`

`九龙灌浴开放时间` 的当前首条检索结果命中结构化景点字段：

`scenic_spot / 九龙灌浴`，包含位置、参数、介绍、亮点、演艺/开放信息等字段。

## 代码修复点

1. `.docx` 知识导入改为读取段落和表格，不再丢失表格知识。
2. 结构化景点导入支持多表独立表头识别，跳过重复表头，避免导入 `spot_code=景点ID` 的伪景点。
3. `.xlsx` 行为数据导入支持当前文件字段：`tourist_id`、`attraction_name`、`visit_date`、`ticket_cost`、`total_cost` 等。
4. `.xlsx` 可作为知识文档导入，生成按景点聚合的门票、消费、满意度、停留时长摘要。
5. RAG 检索增加关键词兜底和 `scenic_spot` 结构化字段检索；即使在线 embedding 查询失败，也能基于本地知识切片回答。
6. 增加同步脚本：`backend/scripts/sync_knowledge_base_from_data.py`。

## 验证命令

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe -m pytest tests -q
```

结果：`49 passed, 25 skipped`。
