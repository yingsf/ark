---
name: ark-sync
description: |
  同步代码现实和 Artifact 现实，识别失真状态，提出需要修正的文档更新动作。
  触发时机：中断恢复时怀疑文档已过期、代码已推进但 docs 未同步、大改动后需要统一校对时。
  关键词：同步、sync、文档过期、状态不一致、恢复上下文、校对状态、文档失真。
version: "1.0"
---

# /ark-sync

## 目标
同步「代码现实」和「Artifact 现实」，识别失真状态，并提出需要修正的文档更新动作。

## 适用场景
- 中断恢复时怀疑文档已过期
- 代码已推进，但 docs 可能未同步
- tasks、plan、handoff 之间存在不一致
- 大改动后需要统一校对状态

## 不适用场景
- 刚完成一次小改动，状态非常清晰
- 当前只需要立刻做一个窄小实现动作
- 没有可供比对的 Artifact 或仓库上下文

## 输入
- 当前仓库状态、`docs/ark/plan.md`、`docs/ark/tasks.md`、`docs/ark/validation.md`、`docs/ark/handoff.md`

## 输出
- 当前状态一致性评估、已发现的冲突或过期内容、建议更新的 Artifact 列表、推荐下一步 Skill

## 相关 Artifact
- 可读取全部 docs Artifact
- 在必要且明确时，可小幅回写：`docs/ark/plan.md`、`docs/ark/tasks.md`、`docs/ark/handoff.md`
- 对 `docs/ark/validation.md` 与 `docs/ark/decisions.md`，更偏向建议更新

## Artifact 可信度判断

sync 执行时，对每个核心 Artifact 判断可信度（定义见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-roles.md`）：

**fresh**：
  - tasks.md 中的任务状态与文件现实一致
  - plan.md 描述的阶段与 tasks.md 完成情况匹配
  - validation.md 覆盖的验证项与当前代码状态一致

**stale**：
  - 文件变更影响该 Artifact，但 Artifact 未反映
  - handoff.md 记录的"下一步"与当前 tasks.md Doing 状态不匹配

**conflicting**：
  - plan.md 与 tasks.md 步骤/任务数不匹配
  - design.md 描述的架构与实际代码结构不符
  - spec.md 的 scope 与 plan.md 的 scope 不一致

**unknown**：
  - Artifact 无版本头（旧项目）
  - 刚接手项目，无法验证一致性
  - 无足够证据判断

判断依据（按优先级）：
  1. 当前文件现实
  2. Artifact 之间一致性
  3. 已执行验证记录
  4. git diff / git log（如可用）

无 git 项目依据 1-3 即可判断，不必然 unknown。

## 版本头检测

检查每个 Artifact 顶部是否有版本头注释：
```
<!-- ark-artifact: <name> -->
<!-- schema-version: X.Y -->
```

- 无版本头 → 标记 unknown，建议重新执行对应 Skill 或手动补充
- 版本低于当前插件 → 提示格式差异，但不自动修改

## 职责边界

ark-sync 只判断状态一致性，职责严格限定为：
- Artifact 之间是否矛盾
- Artifact 与当前文件现实是否匹配
- Artifact 版本头是否存在
- 任务状态与代码变更是否反映

ark-sync **不做**：
- 代码质量评审（那是 ark-review）
- 功能正确性验证（那是 ark-validate）
- 代码结构分析（那是 ark-analyze）
- 无法确认时标 unknown，不做深度推断

## 工作流
1. 读取关键 Artifact，优先查看 `plan`、`tasks`、`validation`、`handoff`。
2. 检查代码与文档是否描述同一阶段。
3. 检查任务状态是否过期。
4. 检查是否存在「实现已完成但未验证」或「handoff 仍停留在旧阶段」的情况。
5. 依据一致性判例表输出结论。
6. 指出需要更新的具体文件与原因。
7. 推荐下一步动作。
8. 如状态非常明确且改动很小，可在严格白名单内直接修正（见下文"可直接修正范围"）。
9. 扫描项目源代码目录结构（根据项目布局：src/ 下的子目录，或根目录下的包目录），当模块数 >= 3 时生成项目地图摘要。

## 一致性判例表

| 等级 | 判例 |
|------|------|
| **一致** | tasks Doing 与 handoff 推荐下一步相符；plan 当前阶段与最近代码改动吻合；validation 对最近完成项有记录 |
| **基本一致** | handoff 比实际进度落后一小步；tasks 中少量状态未更新但不影响当前判断；validation 略滞后但当前阶段仍可识别 |
| **明显失真** | handoff 与 tasks 对当前阶段判断相反；代码已出现实质实现但 plan/tasks 停留在更早阶段；Done 项缺验证记录且已影响下一步判断 |

## 可直接修正范围

**允许直接修正**（仅限状态字段更新，不改变语义内容）：
- `plan.md` 的当前状态字段（Status / Current phase / Last updated）
- `tasks.md` 的单条状态迁移（如 Todo → Doing、Doing → Done）；其中 Doing → Done 仅在已有对应验证记录或验证已明确完成时允许直接修正
- `handoff.md` 的过期标注或最近阶段描述

**不允许直接修正**（只能建议更新）：
- `spec.md`、`design.md`（需求与设计的变更必须经过对应 Skill）
- `validation.md` 的验证事实（验证记录必须真实执行）
- `decisions.md` 的技术判断（决策变更必须经过 `/ark:ark-decide`）

## 验证要求
- 区分「明确冲突」与「可能过期」
- 不凭空捏造未观察到的实现状态
- 若无法判断，应明确写「不确定」

## 停止条件
- 当前状态是否可信已被说明清楚
- 需要更新的 Artifact 已被指出
- 后续建议动作已明确

## 固定输出格式

### 1. 当前状态判断
一致 / 基本一致 / 明显失真

### 1.5 Artifact 可信度矩阵

| Artifact | 可信度 | 判断依据 | 建议 |

### 2. 已发现问题
文档过期项、状态冲突项、缺失验证项、可疑 handoff 项

### 3. 建议更新的 Artifact
需要更新的文件及原因

### 4. 推荐下一步
当前最合理的动作与推荐使用的 Skill

### 5. 项目地图（可选）
当项目源代码中有 3+ 模块时生成，建议补充到 CLAUDE.md 的 Architecture Notes 部分。

## 备注
`/ark:ark-sync` 不替代 spec、plan、validate 或 handoff，它的职责是让整个状态面重新可信。
