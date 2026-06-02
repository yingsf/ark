# Artifact Update Policy

本文件定义 ark 中各 Artifact 的回写条件与禁止性约束。
各 Artifact 的职责边界与「不应用于」说明见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-roles.md`。
扩展文档不属于核心 Artifact，其写入规则见 `${CLAUDE_PLUGIN_ROOT}/rules/extension-doc-policy.md`。

## 核心原则

- **谁最了解这部分状态，谁来更新**：尽量保持回写职责与执行职责一致
- **文档不是装饰**：如果 Artifact 长期不维护，必须明确指出其陈旧状态，而不是假装有效
- **状态冲突必须显式化**：发现代码现实与文档现实不一致，必须先指出冲突，再修正，不得默认一致
- **核心命题必须传递**：spec 中确认的核心命题与不变量，应在 design、plan 和关键 tasks 中持续可见
- **Done 必须由验证闭环支撑**：实现完成但未验证的任务应进入 `Ready for validation`；只有已有 `validation.md` 证据时才能进入 `Done`

---

## Artifact 日期更新协议

当任一 Skill 修改核心 Artifact 内容时：

- 必须将头部 `last-updated` 设置为当前会话真实日期
- 若当前头部日期已经是当天日期，不再改变
- 不得把 `last-updated` 当作版本号递增
- 不得为了表示多次更新而写入明天或未来日期
- 只读取、检查、建议但未修改 Artifact 内容时，不更新 `last-updated`
- `schema-version` 不随内容更新变化，只有 Artifact 模板结构升级时才修改

`last-updated` 只提供跨日期的粗粒度 freshness 信号。同一天内的先后顺序应依据 git history、文件 diff、内容一致性或显式变更记录判断。

---

## 各 Artifact 的回写条件

### `docs/ark/plan.md`

主更新者：`/ark:ark-plan`

以下 Skill 在满足条件时可小幅回写：
- `/ark:ark-implement`：发现原计划与现实明显偏差 / 执行顺序发生实质变化 / 风险或阻塞出现重大变化
- `/ark:ark-debug`：根因导致原计划失效
- `/ark:ark-sync`：plan 已明显失真

**不应用于**：代替 tasks 管理细粒度状态 · 代替 handoff 做恢复摘要

---

### `docs/ark/tasks.md`

主更新者：`/ark:ark-tasks`

以下 Skill 在满足条件时可小幅更新：
- `/ark:ark-implement`：一个任务开始 / 实现已完成并进入 `Ready for validation` / 当前进行中的任务已变化 / 新阻塞已出现
- `/ark:ark-validate`：验证通过后将对应任务从 `Ready for validation` 迁移到 `Done`，并补充 `validation.md` 记录引用
- `/ark:ark-debug`：新的阻塞或诊断任务出现
- `/ark:ark-sync`：tasks 状态明显过期；仅在已有验证记录时修正为 `Done`

**不应用于**：代替 spec 定义需求 · 代替 plan 定义阶段策略

---

### `docs/ark/decisions.md`

主更新者：`/ark:ark-decide`

`decisions.md` 是项目级长期记忆和当前仍有效决策索引，不是阶段局部任务记录。阶段切换时不得把它当作普通阶段文档清空。

以下 Skill 在满足条件时可建议更新（不直接回写，建议用户确认）：
- `/ark:ark-implement`：出现关键技术取舍
- `/ark:ark-debug`：修复路径引入重要取舍
- `/ark:ark-refactor`：重构引入不可逆的结构性选择
- `/ark:ark-stage`：阶段切换时分类长期决策、阶段性决策和已替代决策；不确定时默认保留

---

### `docs/ark/validation.md`

主更新者：`/ark:ark-validate`

只记录**真实执行过**的验证内容，禁止将「计划验证」写成「已执行验证」。

---

### `docs/ark/handoff.md`

主更新者：`/ark:ark-handoff`

以下情况可触发更新建议：
- `/ark:ark-sync`：handoff 与当前阶段明显不符
- `/ark:ark-next`：handoff 是推荐下一步的主要信息来源，若过期应标注

**不应用于**：代替 plan 作为主执行文档 · 代替 tasks 管理状态

---

### `docs/ark/stages.md` 与 `docs/ark/archive/<stage-id>/`

主更新者：`/ark:ark-stage`

`docs/ark/stages.md` 是阶段索引，不属于初始化默认 7 个核心 Artifact。`docs/ark/archive/<stage-id>/` 保存阶段归档，不作为当前执行依据。

`/ark:ark-stage` 在以下模式中可写：
- `stage-close`：归档当前 7 个 Artifact，生成 `stage-summary.md`，更新 `stages.md`
- `stage-open`：重建当前 7 个 Artifact，更新 `stages.md`
- `stage-transition`：执行 close + open 的组合写入

除只读 `stage-status` 外，`ark-stage` 必须先输出 preview 并等待用户确认。存在 Blocked、Ready for validation、Done 缺 validation、handoff 与 tasks 冲突、plan 当前状态过期时，不得静默写成 `closed`；用户确认带风险进入下一阶段时，状态写为 `closed-with-risk`，并写入 Carryover Gates。

`ark-stage` 对 `decisions.md` 的处理必须遵循项目级长期记忆规则：`stage-close` 只归档历史快照；`stage-open` / `stage-transition` 不得生成空的 `decisions.md`；仍有效的长期决策继续保留；已被替代的长期决策标记为 `superseded` / 已替代；阶段性决策仅在明确不再约束新阶段时才只保留在 archive。

`ark-stage` 禁止写源代码、测试代码、项目配置、`.data/`、真实数据内容、密钥或连接串。

---

### `docs/ark/spec.md` / `docs/ark/design.md`

主更新者分别为 `/ark:ark-spec` 和 `/ark:ark-design`。

`/ark:ark-analyze` 可在首次分析时预填充这两个文件（基于代码扫描结果反推）。预填充条件：
- 文件为空或仍为初始模板内容
- 基于代码实际行为和结构反推，不凭空编写
- 必须标注来源（`<!-- 由 /ark:ark-analyze 自动生成，需人工确认 -->`）
- 后续应由 `/ark:ark-spec` 或 `/ark:ark-design` 审查确认

其他 Skill 通常不直接回写这两个文件。如发现内容过期，应建议重新执行对应 Skill，而不是随意修改。

`spec.md` 应定义核心命题与不变量；`design.md` 应说明技术方案如何承接这些命题与不变量。若后续 Artifact、扩展文档或代码现实弱化了这些约束，应标记 stale/conflicting 并建议执行对应 Skill。

允许其他 Skill 识别并报告 spec/design 漂移，但不得直接落盘：
- `/ark:ark-implement`：本次实现改变能力范围、验收标准、外部接口、MCP/API 契约、模块边界、数据流、运行时机制、资源生命周期、并发/降级策略时，建议 `/ark:ark-spec` 或 `/ark:ark-design`
- `/ark:ark-debug`：修复 bug 时发现原需求边界、验收标准、错误语义、降级策略或设计假设不成立时，建议 `/ark:ark-spec` 或 `/ark:ark-design`
- `/ark:ark-refactor`：重构改变模块边界、依赖方向、接口组织、资源生命周期等设计现实，或发现“不变行为”边界实际不清时，建议 `/ark:ark-design` 或 `/ark:ark-spec`
- `/ark:ark-sync`：全局一致性检查中发现 spec/design 与代码现实、plan、tasks 或 validation 冲突时，标记 stale/conflicting 并建议对应 Skill

---

## 扩展文档回写条件

扩展文档包括 `docs/solution/*`、`docs/design/*`、`docs/contracts/*`、`docs/integrations/*`、`docs/data-sources/*`、`docs/operations/*`、`docs/runbooks/*`、`docs/migration/*`、`docs/security/*`、`docs/research/*`、`docs/examples/*` 等项目自有文档。

主更新者：`/ark:ark-solution`

允许更新：
- 专题详细方案
- 模块级或组件级详细设计
- HTTP/MCP/API/CLI/SDK/文件格式/事件契约
- 外部系统集成说明
- 数据源元信息（位置、格式、脱敏状态、样例范围、访问方式），不包含数据内容
- 运维、迁移、安全、调研、示例等专题文档

其他 Skill 通常只识别扩展文档漂移并建议更新：
- `/ark:ark-implement`：实现改变专题方案、详细设计、接口契约、集成方式或数据源使用方式时，建议 `/ark:ark-solution`
- `/ark:ark-debug`：修复证明扩展文档中的失败语义、契约、集成假设或数据说明过期时，建议 `/ark:ark-solution`
- `/ark:ark-refactor`：重构改变模块级详细设计或契约组织时，建议 `/ark:ark-solution`
- `/ark:ark-sync`：检查扩展文档索引与文件现实，输出可信度摘要并建议 `/ark:ark-solution`
- `/ark:ark-design`：维护 `docs/ark/design.md` 中的扩展文档索引和全局摘要，不代替 `/ark:ark-solution` 写专题正文

禁止：
- 把扩展文档正文写入 `docs/ark/spec.md` 或 `docs/ark/design.md`
- 把 `data-sources` 当成数据托管目录
- 将探索性 research 文档直接当作 active 设计依据，除非已被 spec/design 或 decisions 确认

---

## 实施过程中的回写规则

### `/ark:ark-implement`
- 原计划与现实偏差明显 → 更新 `docs/ark/plan.md`
- 某项任务开始 / 实现完成待验证 / 阻塞 → 更新 `docs/ark/tasks.md`
- 实现完成但未由 `/ark:ark-validate` 记录验证证据 → 将任务置为 `Ready for validation`，不得置为 `Done`
- 每轮 implement 必须先锁定本轮唯一执行目标；未指定 task、batch 或阶段范围时，不得连续执行多个 Todo
- 出现关键技术取舍 → 建议更新 `docs/ark/decisions.md`（不强制直接写入）
- 本次实现改变需求范围、验收标准、对外能力或非目标边界 → 建议 `/ark:ark-spec`，不直接回写 `docs/ark/spec.md`
- 本次实现改变模块边界、接口契约、数据流、运行时机制、资源生命周期、并发/降级策略 → 建议 `/ark:ark-design`，不直接回写 `docs/ark/design.md`
- 本次实现改变专题方案、详细设计、接口契约、集成方式、数据源元信息或替身边界 → 建议 `/ark:ark-solution`，不直接回写扩展文档

**plan.md 回写触发样例：**

应触发：
- 原计划 1 阶段能完成，现发现必须拆成多阶段
- 原先假定不需要 DB migration，现确认必须做
- 原计划执行顺序需要实质性调整

不应触发：
- 单个函数实现细节微调
- 局部命名调整
- 不影响阶段推进顺序的小修正

**tasks.md 回写触发样例：**

应触发：
- Todo → Doing（任务开始）
- Doing → Ready for validation（实现完成但未验证）
- Ready for validation → Done（验证已完成且 `validation.md` 有记录；通常由 `/ark:ark-validate` 触发）
- Doing → Blocked（遇到阻塞）
- 新增一个必须先完成的前置任务

状态迁移原子性：
- 状态迁移必须是移动而不是复制
- 同一个 task ID 不得跨状态重复出现
- 回写后必须自检 task ID 唯一性；若发现重复或无法安全迁移，应停止并建议 `/ark:ark-sync`
- 未纳入本轮唯一执行目标或当前批次边界的 task 不得被顺手更新状态

不应触发：
- 仅仅阅读了一个文件
- 没有客观完成标准的模糊进展

### `/ark:ark-debug`
- 根因导致原计划失效 → 更新 `docs/ark/plan.md`
- 新的阻塞或诊断任务出现 → 更新 `docs/ark/tasks.md`
- 修复路径引入重要取舍 → 建议更新 `docs/ark/decisions.md`
- 修复暴露需求边界、验收标准、错误语义或设计假设过期 → 建议 `/ark:ark-spec` 或 `/ark:ark-design`
- 修复证明扩展文档中的专题方案、契约、集成假设或数据源说明过期 → 建议 `/ark:ark-solution`

### `/ark:ark-refactor`
- 重构范围超出预期 → 更新 `docs/ark/plan.md`
- 任务状态变化 → 更新 `docs/ark/tasks.md`
- 引入不可逆结构性选择 → 建议更新 `docs/ark/decisions.md`
- 重构改变设计现实但不改变需求承诺 → 建议 `/ark:ark-design`
- 重构过程中发现外部行为或能力边界实际发生变化 → 停止扩大重构范围，建议 `/ark:ark-spec` 或 `/ark:ark-design` 重新确认
- 重构改变扩展文档覆盖的模块级详细设计、契约组织或专题方案 → 建议 `/ark:ark-solution`

### `/ark:ark-review`
- 发现严重问题导致计划需要调整 → 建议更新 `docs/ark/plan.md`
- review 结论影响验证策略 → 建议更新 `docs/ark/validation.md`

### `/ark:ark-validate`
- 真实执行验证并写入 `docs/ark/validation.md`
- 验证通过且能对应到 `tasks.md` 的 Ready for validation 项 → 可将任务迁移到 Done，并写入 validation 章节引用
- 验证失败 → 保持 Ready for validation 或转 Blocked，记录失败事实、复现条件和建议 `/ark:ark-debug`

### `/ark:ark-sync`
优先指出并修正以下情况：
- docs 与代码现实冲突
- tasks 状态明显过期
- plan 已失真
- handoff 与当前阶段不符
- validation 漏记关键结果
- Ready for validation 项缺少验证结论
- Done 项缺少 `validation.md` 引用
- spec/design/plan/tasks 对核心命题与不变量的承接断裂
- spec.md 的范围、能力承诺、验收标准、外部接口与代码现实或 plan/tasks 不一致
- design.md 的模块结构、接口边界、数据流、关键运行机制与代码现实不一致
- design.md 的扩展文档索引与项目实际扩展文档不一致
- 扩展文档正文与核心 Artifact 或代码现实不一致

### `/ark:ark-stage`
- 阶段收口 / 归档 / 开启新阶段前必须先审计 7 个核心 Artifact、`stages.md`（如存在）和 archive（如需要）
- `stage-status` 只读，不回写任何文件
- `stage-close` / `stage-open` / `stage-transition` 必须先 preview 并等待用户确认
- 归档时原样复制当前 7 个核心 Artifact 到 `docs/ark/archive/<stage-id>/`，并生成 `stage-summary.md`
- 开启新阶段时重建当前 7 个 Artifact，但不得把旧阶段 validation 原样继承为新阶段已通过；只能继承为验证基线、历史证据、可复用检查项、未覆盖风险或下一阶段门禁
- 未闭合项如需带入下一阶段，必须写入 Carryover Gates，不得静默删除

### `/ark:ark-analyze`
- 首次分析已有代码库 → 预填充 `docs/ark/spec.md`（当前系统在做什么）
- 首次分析已有代码库 → 预填充 `docs/ark/design.md`（当前架构长什么样）
- 预填充内容必须标注来源，后续应由 `/ark:ark-spec` 或 `/ark:ark-design` 审查确认

---

## 禁止性约束

1. **没有验证记录，不宣称完成**：中大型任务如无验证记录，不得写出「已完成且无风险」的结论
2. **Done 不得绕过 validate**：实现完成但未验证的任务不得标记为 Done，应使用 Ready for validation
3. **handoff 不是 plan 的替代品**：handoff 是恢复视图，不是执行主文档
4. **tasks 不是 spec 的替代品**：任务列表不能代替需求定义
5. **plan 不是 validation 的替代品**：计划中的「准备怎么验」不能等同于「已经验证」
6. **冲突必须先显式化**：若发现文档与实现冲突，必须先指出冲突，再修正，不得直接跳过
7. **不得将推测写成结论**：所有 Artifact 内容必须区分事实与推断
8. **核心 Artifact 不承载扩展正文**：详细方案、专题设计、契约、数据源元信息等不得塞入 `docs/ark/*`
9. **不得托管项目数据**：ARK 只记录数据源元信息和验证证据，不写入敏感数据或大体量数据内容

---

## 最低维护要求

| 任务规模 | 最低要求 |
|---------|----------|
| Small | 必要时更新 `docs/ark/validation.md` |
| Medium | `docs/ark/plan.md` + `docs/ark/validation.md` |
| Large | 全部 7 个核心 Artifact |
