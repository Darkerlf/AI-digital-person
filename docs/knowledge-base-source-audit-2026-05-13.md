# 知识库与源文档一致性审计

审计时间：2026-05-13

源目录：`D:\AI digital person\.worktrees\admin-backend-phase1\data`

## 结论

当前知识库没有完全匹配源目录中的三份景点知识文档。

主要差异：

1. 两份 `.docx` 虽然都存在于 `knowledge_document`，但当前知识导入器只读取普通段落，没有读取表格内容。
2. `灵山胜境 景点结构化数据集.docx` 的核心内容几乎全部在表格中，约 16941 字表格内容没有进入 RAG 知识切片。
3. `灵山胜境：历史、文化、景点特色与个性化游览指南.docx` 中约 1732 字表格内容没有进入 RAG 知识切片。
4. `景点景区旅游数据行为分析数据.xlsx` 没有作为知识文档导入，也没有导入到游客行为事件表。
5. 结构化景点表已进入 `scenic_spot`，但 RAG 当前只检索 `knowledge_chunk` 和 `faq_item`，不会使用 `scenic_spot` 表回答游客问答。
6. `faq_item` 当前为 0 条，高频问题没有兜底知识。

## 源文件清单

| 文件 | 类型 | 大小 |
| --- | --- | ---: |
| 景点景区旅游数据行为分析数据.xlsx | xlsx | 16740760 bytes |
| 灵山胜境 景点结构化数据集.docx | docx | 45476 bytes |
| 灵山胜境：历史、文化、景点特色与个性化游览指南.docx | docx | 30179 bytes |

## 当前数据库概况

| 项目 | 数量 |
| --- | ---: |
| knowledge_document | 2 |
| knowledge_chunk | 8 |
| 已有 embedding 的 chunk | 8 |
| faq_item | 0 |
| scenic_spot | 23 |
| visitor_behavior_event | 0 |

## DOCX 对照结果

| 源文档 | 源段落字数 | 源表格字数 | 源全文字数 | DB 文档字数 | 是否匹配段落 | 是否匹配全文 | chunk 数 |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| 灵山胜境 景点结构化数据集.docx | 262 | 16941 | 17204 | 262 | 是 | 否 | 1 |
| 灵山胜境：历史、文化、景点特色与个性化游览指南.docx | 4168 | 1732 | 5901 | 4168 | 是 | 否 | 7 |

说明：当前 `KnowledgeDocImporter` 使用 `read_docx_paragraphs()`，该函数只读取 `document.paragraphs`，不会读取 `document.tables`。因此两个知识文档的数据库文本都只匹配源文档中的段落部分，不匹配包含表格的完整源文档。

## 结构化景点数据对照

`灵山胜境 景点结构化数据集.docx` 实际包含 2 张表：

| 表 | 行数 | 说明 |
| --- | ---: | --- |
| 表 1 | 17 | 1 行表头 + 16 条灵山胜境景点 |
| 表 2 | 7 | 1 行表头 + 6 条拈花湾景点 |

实际源数据景点行数：22。

数据库 `scenic_spot` 行数：23。

多出的数据库记录：

| spot_code | name |
| --- | --- |
| 景点ID | 景点名称 |

原因判断：当前 `ScenicDocxImporter` 将整个 docx 中所有表格行直接展开，并只使用第一张表的表头；第二张表的表头被当成了一条普通景点数据导入。

已匹配的 22 条源景点数据中，字段级对照未发现差异，字段包括：

- 具体位置
- 建筑/景观参数
- 核心功能
- 文化内涵
- 详细介绍
- 游玩亮点
- 演艺/开放信息
- 备注

但这些字段目前只存在于 `scenic_spot` 表，不会进入 RAG 检索上下文。

## XLSX 对照结果

文件：`景点景区旅游数据行为分析数据.xlsx`

| 项目 | 结果 |
| --- | --- |
| 工作表 | 景点景区旅游数据行为分析数据 |
| 总行数 | 140448 |
| 数据行估算 | 140447 |
| 列数 | 17 |
| 是否存在于 knowledge_document | 否 |
| visitor_behavior_event 行数 | 0 |

表头字段：

`tourist_id`, `user_nickname`, `age`, `gender`, `attraction_name`, `attraction_content`, `attraction_type`, `visit_date`, `stay_duration`, `ticket_cost`, `food_cost`, `shopping_cost`, `transport_cost`, `entertainment_cost`, `total_cost`, `group_size`, `satisfaction`

该文件含有 `ticket_cost`、`total_cost` 等费用字段，但当前没有进入知识库或行为事件库，因此问答无法基于它回答费用类问题。

## 关键词覆盖情况

当前 RAG 知识文本中存在的关键词数量：

| 关键词 | 次数 |
| --- | ---: |
| 门票 | 2 |
| 票价 | 0 |
| 价格 | 4 |
| 开放时间 | 0 |
| 灵山大佛 | 22 |
| 九龙灌浴 | 16 |
| 梵宫 | 28 |
| 停车 | 0 |
| 讲解 | 18 |

对比源文档可见，部分关键词存在于源文档表格中，但没有进入知识切片。例如 `灵山胜境 景点结构化数据集.docx` 源全文中 `门票` 出现 3 次、`开放时间` 出现 5 次，但数据库该知识文档正文中均为 0 次。

## 影响

当前小程序问答出现“门票价格在参考资料中未提到”是符合当前数据库状态的：RAG 能检索的 `knowledge_chunk` 中缺少完整表格知识，FAQ 为空，xlsx 费用数据也未导入。

即使 `scenic_spot` 表里已有部分景点字段，当前 `RAGPipeline.retrieve()` 只检索：

- `knowledge_chunk`
- `faq_item`

不会检索：

- `scenic_spot`
- `visitor_behavior_event`
- xlsx 派生统计

## 修复建议

1. 修复 `read_docx_paragraphs()` 或新增 `read_docx_blocks()`，在知识导入时同时读取段落和表格，并尽量保留文档顺序。
2. 修复 `ScenicDocxImporter` 的多表解析逻辑，每张表独立识别表头，跳过所有表头行，避免再次导入 `spot_code=景点ID` 的伪数据。
3. 将结构化景点数据同步生成 RAG 知识切片，或让 RAG 检索链路支持 `scenic_spot` 表。
4. 为 xlsx 建立单独导入策略：原始 140447 行不建议直接逐行进入 RAG，应导入行为表并生成可问答的聚合知识，例如各景点平均票务/消费/满意度/停留时长。
5. 清理当前错误景点记录 `spot_code=景点ID`。
6. 重新导入两份 docx、重建 chunks、重新生成 embeddings。
7. 补充审计测试，确保源文件段落、表格、结构化行数、知识切片数量可自动对账。
