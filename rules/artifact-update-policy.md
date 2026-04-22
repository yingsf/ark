# Artifact Update Policy

本文件定义 ark 中各 Artifact 的回写条件与禁止性约束。
各 Artifact 的职责边界与「不应用于」说明见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-roles.md`。

## 核心原则

- **谁最了解这部分状态，谁来更新**：尽量保持回写职责与执行职责一致
- **文档不是装饰**：如果 Artifact 长期不维护，必须明确指出其陈旧状态，而不是假装有效
- **状态冲突必须显式化**：发现代码现实与文档现实不一致，必须先指出冲突，再修正，不得默认一致

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
- `/ark:ark-implement`：一个任务实际已完成 / 当前进行中的任务已变化 / 新阻塞已出现
- `/ark:ark-debug`：新的阻塞或诊断任务出现
- `/ark:ark-sync`：tasks 状态明显过期

**不应用于**：代替 spec 定义需求 · 代替 plan 定义阶段策略

---

### `docs/ark/decisions.md`

主更新者：`/ark:ark-decide`

以下 Skill 在满足条件时可建议更新（不直接回写，建议用户确认）：
- `/ark:ark-implement`：出现关键技术取舍
- `/ark:ark-debug`：修复路径引入重要取舍
- `/ark:ark-refactor`：重构引入不可逆的结构性选择

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

### `docs/ark/spec.md` / `docs/ark/design.md`

主更新者分别为 `/ark:ark-spec` 和 `/ark:ark-design`。

`/ark:ark-analyze` 可在首次分析时预填充这两个文件（基于代码扫描结果反推）。预填充条件：
- 文件为空或仍为初始模板内容
- 基于代码实际行为和结构反推，不凭空编写
- 必须标注来源（`<!-- 由 /ark:ark-analyze 自动生成，需人工确认 -->`）
- 后续应由 `/ark:ark-spec` 或 `/ark:ark-design` 审查确认

其他 Skill 通常不直接回写这两个文件。如发现内容过期，应建议重新执行对应 Skill，而不是随意修改。

---

## 实施过程中的回写规则

### `/ark:ark-implement`
- 原计划与现实偏差明显 → 更新 `docs/ark/plan.md`
- 某项任务完成 / 开始 / 阻塞 → 更新 `docs/ark/tasks.md`
- 出现关键技术取舍 → 建议更新 `docs/ark/decisions.md`（不强制直接写入）

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
- Doing → Done（任务完成且验证已完成）
- Doing → Blocked（遇到阻塞）
- 新增一个必须先完成的前置任务

不应触发：
- 仅仅阅读了一个文件
- 没有客观完成标准的模糊进展

### `/ark:ark-debug`
- 根因导致原计划失效 → 更新 `docs/ark/plan.md`
- 新的阻塞或诊断任务出现 → 更新 `docs/ark/tasks.md`
- 修复路径引入重要取舍 → 建议更新 `docs/ark/decisions.md`

### `/ark:ark-refactor`
- 重构范围超出预期 → 更新 `docs/ark/plan.md`
- 任务状态变化 → 更新 `docs/ark/tasks.md`
- 引入不可逆结构性选择 → 建议更新 `docs/ark/decisions.md`

### `/ark:ark-review`
- 发现严重问题导致计划需要调整 → 建议更新 `docs/ark/plan.md`
- review 结论影响验证策略 → 建议更新 `docs/ark/validation.md`

### `/ark:ark-sync`
优先指出并修正以下情况：
- docs 与代码现实冲突
- tasks 状态明显过期
- plan 已失真
- handoff 与当前阶段不符
- validation 漏记关键结果

### `/ark:ark-analyze`
- 首次分析已有代码库 → 预填充 `docs/ark/spec.md`（当前系统在做什么）
- 首次分析已有代码库 → 预填充 `docs/ark/design.md`（当前架构长什么样）
- 预填充内容必须标注来源，后续应由 `/ark:ark-spec` 或 `/ark:ark-design` 审查确认

---

## 禁止性约束

1. **没有验证记录，不宣称完成**：中大型任务如无验证记录，不得写出「已完成且无风险」的结论
2. **handoff 不是 plan 的替代品**：handoff 是恢复视图，不是执行主文档
3. **tasks 不是 spec 的替代品**：任务列表不能代替需求定义
4. **plan 不是 validation 的替代品**：计划中的「准备怎么验」不能等同于「已经验证」
5. **冲突必须先显式化**：若发现文档与实现冲突，必须先指出冲突，再修正，不得直接跳过
6. **不得将推测写成结论**：所有 Artifact 内容必须区分事实与推断

---

## 最低维护要求

| 任务规模 | 最低要求 |
|---------|----------|
| Small | 必要时更新 `docs/ark/validation.md` |
| Medium | `docs/ark/plan.md` + `docs/ark/validation.md` |
| Large | 全部 7 个核心 Artifact |
