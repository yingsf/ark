# Extension Doc Policy

本文件定义 ARK 如何支持核心 Artifact 之外的专题方案、详细设计、契约和其他扩展文档。

## 核心原则

`docs/ark/` 只保留 7 个核心 Artifact：

- `spec.md`
- `design.md`
- `plan.md`
- `tasks.md`
- `decisions.md`
- `validation.md`
- `handoff.md`

详细方案、专题设计、接口契约、数据源说明等不应塞进 `docs/ark/`，也不应让 `spec.md` / `design.md` 变成大型文档库。它们应放在项目自有文档目录中，并由 `docs/ark/design.md` 建立索引和当前可信度摘要。

## 扩展文档类型

按需创建，不默认铺满目录：

| 类型 | 默认目录 | 用途 |
|------|----------|------|
| solution | `docs/solution/` | 某个功能、阶段或专题的详细解决方案 |
| design | `docs/design/` | 模块级、组件级或子系统详细设计 |
| contracts | `docs/contracts/` | HTTP/MCP/API/CLI/SDK/文件格式/事件契约 |
| integrations | `docs/integrations/` | 外部系统接入、认证、配置、失败语义 |
| data-sources | `docs/data-sources/` | 数据源元信息、样例范围、脱敏状态、访问方式；不存放数据内容 |
| operations / runbooks | `docs/operations/` 或 `docs/runbooks/` | 启动、部署、排障、运维操作 |
| migration | `docs/migration/` | 数据迁移、兼容性迁移、版本升级路径 |
| security | `docs/security/` | 权限、安全边界、密钥、审计、威胁模型 |
| research | `docs/research/` | 探索、调研、Spike 结论；需标注非权威或待确认 |
| examples | `docs/examples/` | 可执行示例、使用场景、样例输入输出说明 |

用户可按项目习惯调整目录；但 `docs/ark/` 不承载这些扩展文档正文。

## ark-solution 职责

`/ark:ark-solution` 是扩展文档的主写入者。它可创建或更新扩展文档，但不得直接写入核心 Artifact。

允许写入：
- `docs/solution/*`
- `docs/design/*`
- `docs/contracts/*`
- `docs/integrations/*`
- `docs/data-sources/*`
- `docs/operations/*`
- `docs/runbooks/*`
- `docs/migration/*`
- `docs/security/*`
- `docs/research/*`
- `docs/examples/*`

不得直接写入：
- `docs/ark/spec.md`
- `docs/ark/design.md`
- `docs/ark/plan.md`
- `docs/ark/tasks.md`
- `docs/ark/decisions.md`
- `docs/ark/validation.md`
- `docs/ark/handoff.md`

若扩展文档影响核心 Artifact，`ark-solution` 只能在输出中建议：
- 范围、验收、能力承诺变化 → `/ark:ark-spec`
- 全局设计摘要或扩展文档索引需要更新 → `/ark:ark-design`
- 关键取舍需要记录 → `/ark:ark-decide`
- 需要拆解执行 → `/ark:ark-plan` 或 `/ark:ark-tasks`

## 扩展文档头

扩展文档建议包含轻量头部，便于 sync 和 design 索引：

```markdown
<!-- ark-extension-doc: <type> -->
<!-- ark-related-artifacts: docs/ark/spec.md, docs/ark/design.md -->
<!-- ark-status: draft / active / stale / superseded -->

# <Title>
```

`draft` 表示探索或未确认；`active` 表示当前有效；`stale` 表示需更新；`superseded` 表示已被其他文档取代。

## 与 design.md 的关系

`docs/ark/design.md` 仍负责全局设计摘要。它应在"扩展文档索引"中记录：

- 扩展文档路径
- 类型
- 覆盖的主题
- 当前可信度：fresh / stale / conflicting / unknown
- 与核心 Artifact 的关系

`design.md` 不复制扩展文档正文，只保留摘要和索引。

## 漂移处理

引入扩展文档后，ARK 同时检查三类漂移：

1. `spec.md` 漂移：需求范围、验收标准、能力承诺、外部可见行为变化
2. `design.md` 漂移：全局模块边界、接口契约、数据流、运行机制变化
3. 扩展文档漂移：专题方案、详细设计、契约、数据源说明与代码现实或核心 Artifact 不一致

处理规则：
- `/ark:ark-implement`、`/ark:ark-debug`、`/ark:ark-refactor` 可识别扩展文档漂移，但不得直接更新扩展文档；应建议 `/ark:ark-solution`
- `/ark:ark-sync` 输出扩展文档可信度矩阵，并建议 `/ark:ark-solution` 或 `/ark:ark-design`
- `/ark:ark-design` 维护扩展文档索引，但不代替 `ark-solution` 写专题正文

## 与 ark-intake / ark-docs 的边界

- `/ark:ark-intake` 只澄清、分流、建议落盘位置，不写扩展文档。
- `/ark:ark-docs` 更新 README、用户文档、安装运行说明等一般文档；不承担专题方案、详细设计和契约文档的主写入职责。
- `/ark:ark-solution` 写专题方案、详细设计、契约、集成、数据源元信息等工程决策型扩展文档。

## 非目标

- 不把扩展文档变成新的强制流程。
- 不要求每个项目都创建所有扩展目录。
- 不让扩展文档取代 7 个核心 Artifact。
- 不把 `data-sources` 误解为 ARK 管理数据文件本身。
