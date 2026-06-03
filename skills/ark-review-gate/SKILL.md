---
name: ark-review-gate
description: |
  组织跨智能体外部代码审查门禁，按风险判断当前 task 是立即外部审查，还是进入同闭环小批量审查队列，并生成审查包、导入 findings、生成定向复检包。
  触发时机：ark-implement 完成后需要决定是否去外部智能体审查、准备给 Codex/其他 agent 的审查材料、导入外部 review findings、修复后准备外部复检。
  关键词：外部审查、跨智能体审查、Codex review、review gate、审查门禁、批量审查、复检包、导入 findings。
version: "1.0"
---

# /ark-review-gate

## 目标

在不削弱外部智能体审查质量的前提下，减少低风险 task 的重复审查成本。它只组织外部审查流程，不替代 `/ark:ark-review`，不替代外部 Codex 审查，不修代码，不写 `validation.md`。

核心策略：

```text
高风险不过夜，低风险不单审。
```

## 模式

| 模式 | 触发语义 | 作用 |
|------|----------|------|
| `status` | 判断当前是否该外部审查 | 输出 gate 结论，不生成完整审查包 |
| `prepare` | 准备外部审查 | 生成给 Codex/其他 agent 的初审包或 batch 审查包 |
| `import` | 用户粘贴外部 findings | 分类 findings，形成 `/ark:ark-debug` 修复输入 |
| `recheck` | 修复后准备复检 | 生成只复查上一轮 findings 的定向复检包 |

用户未指定模式时，默认执行 `status`；若已有 Ready for validation task 且需要外部审查包，建议执行 `prepare`。

## 输入

- 用户指定的 task、batch、外部 findings 或复检目标。
- `docs/ark/tasks.md`、`docs/ark/validation.md`、`docs/ark/handoff.md`。
- 相关 `spec.md`、`design.md`、`plan.md`、`decisions.md` 和扩展文档摘要。
- 当前 git diff、已修改文件、已执行测试结果。
- `/ark:ark-implement` 的功能结果、验证状态、风险与回写建议。

## 相关规则

执行时必须遵循：

- `${CLAUDE_PLUGIN_ROOT}/rules/external-review-gate.md`

## 职责边界

- 可以读取代码、Artifact、diff、测试输出和用户粘贴的外部审查结果。
- 可以写入 `docs/ark/handoff.md` 的 External Review Gate 区域，记录 pending batch、gate 结论、审查状态和下一步。
- 不得修改源代码、测试代码、项目配置或依赖文件。
- 不得写入 `docs/ark/validation.md`；外部审查通过证据由 `/ark:ark-validate` 记录。
- 不得把 task 标记为 Done。
- 不得把外部 review findings 直接改成 tasks；Critical / Major 可建议新增 task，但不直接写入。

## Gate 判断

输出结论只能是：

- `immediate`
- `batch-candidate`
- `batch-ready`
- `blocked`

必须说明：

- 风险等级：High / Medium / Low
- 命中规则
- 当前 batch task 列表
- 是否建议继续下一个 task
- 下一步建议

### immediate

命中高风险条件时使用。包括但不限于：认证/权限/安全、支付/账务、数据删除/迁移、数据库 schema、公共 API、并发/事务/缓存/幂等、共享基础设施、CI/发布/安装/更新路径、新增或升级关键依赖、测试失败过、实现报告存在不确定点、上一轮外部审查发现严重问题、跨多个子系统。

### batch-candidate

只有同时满足以下条件才使用：

- 同一个功能闭环、同一 batch、同一真实入口或同一公开契约。
- 不改公共接口、数据库 schema、权限、安全、支付、隐私或共享基础设施。
- 本地相关测试通过。
- 改动范围小，需求和实现方向清楚。
- 没有明显风险、不确定点或替身冒充真实验证。

### batch-ready

任一上限达到即使用：

- 3 个 task。
- 90 分钟实现量。
- 1 个功能闭环结束。
- 500 行核心 diff。
- 用户要求审查。
- batch 内任一 task 后续命中 immediate 条件。

### blocked

材料不足、tasks 状态冲突、无法定位本轮 task、diff 与 tasks 不对应、handoff 与 tasks 冲突时使用。blocked 时先建议 `/ark:ark-sync` 或要求补充材料。

## status 工作流

1. 锁定当前 task 或 batch。
2. 读取 `tasks.md` 中 Ready for validation / Doing / External Review Pending 状态。
3. 读取 `handoff.md` 中已有 External Review Gate 记录。
4. 检查实现报告、diff 和测试结果。
5. 按风险规则输出 gate 结论。
6. 如可进入 batch，建议写入 handoff pending；如必须立即审查，建议执行 `prepare`。

## prepare 工作流

1. 确认 gate 结论：`immediate` 或 `batch-ready`。
2. 生成外部审查包。
3. 审查包必须限制范围：只审当前 task 或同闭环 batch，不重新审查无关历史代码。
4. 明确要求外部智能体输出 Findings、Verification、Open Questions 和 Verdict。
5. 若存在 batch pending，写入或更新 `handoff.md` External Review Gate 区域。

审查包必须包含：

```markdown
## 外部审查包

### 1. 审查目标
- Gate 结论：
- 审查类型：single-task / batch
- 覆盖任务：
- 用户可观察目标：
- 完成信号：

### 2. ARK 上下文
- spec 摘要：
- design 摘要：
- plan/task 摘要：
- decisions 约束：

### 3. 本次改动
- 修改文件：
- 核心 diff 摘要：
- 不属于本次范围：

### 4. 已执行验证
- 命令与结果：
- 未执行验证：
- 替身边界：

### 5. 请重点检查
- 任务契约是否满足
- task 之间是否有状态/接口/测试联动风险
- 测试是否真的证明契约
- 是否存在回归、权限、边界、默认行为或失败路径问题

### 6. 请不要扩展
- 不审查无关历史代码
- 不提出与当前 task 无关的大重构
- 不把 craftsmanship 建议伪装成阻断性 bug

### 7. 外部智能体输出要求
- Findings：Critical / Major / Minor，附文件行号、原因、修复建议、测试缺口
- Verification：执行了哪些检查
- Open Questions：影响判断的信息缺口
- Verdict：pass / needs-fix / blocked
```

## import 工作流

1. 读取用户粘贴的外部 findings。
2. 按“必须修复 / 可延期 / 不处理”分类。
3. 识别是否存在 Critical / Major。
4. 生成 `/ark:ark-debug` 修复输入，只包含必须修复项。
5. 若有 pending batch，更新 `handoff.md` External Review Gate 状态为 `findings-imported`。
6. 若 findings 全部为误报或非阻断，建议 `/ark:ark-validate` 记录外部审查证据。

导入输出必须包含：

```markdown
## Findings 分类

### 必须修复
- Finding:
  来源：
  影响任务：
  修复目标：
  建议验证：

### 可延期
- Finding:
  延期原因：
  建议后续 task：

### 不处理
- Finding:
  不处理原因：

## 建议给 /ark:ark-debug 的输入
...
```

## recheck 工作流

1. 读取上一轮外部 findings 和 `/ark:ark-debug` 修复摘要。
2. 只生成定向复检包。
3. 明确要求外部智能体只复查上一轮 findings 是否闭合，以及修复是否引入明显回归。
4. 除非发现 Critical 新风险，不扩大审查范围。
5. 复检通过后建议 `/ark:ark-validate` 记录证据并推进 Done。

复检包必须包含：

```markdown
## 外部复检包

### 1. 复检目标
- 只复检上一轮 findings：
- 覆盖任务：

### 2. 修复摘要
- 已修复：
- 未修复：
- 延期项：

### 3. 请检查
- 每个必须修复项是否闭合
- 修复是否引入明显回归
- 测试是否覆盖修复点

### 4. 请不要扩展
- 不重新全量审查
- 不新增非阻断 craftsmanship 范围

### 5. 输出要求
- 每个上一轮 finding：closed / still-open / not-applicable
- 新增严重风险：仅限 Critical / Major
- Verdict：pass / needs-fix / blocked
```

## Handoff 写入格式

如需要记录 pending 状态，写入 `docs/ark/handoff.md`：

```markdown
## External Review Gate
- Gate 结论：immediate / batch-candidate / batch-ready / blocked
- 风险等级：High / Medium / Low
- Pending task：T...
- Batch 范围：T... / 无
- 触发上限：3 tasks / 90 minutes / 1 feature loop / 500 core diff lines / user requested / none
- 外部审查状态：pending / package-prepared / findings-imported / recheck-pending / passed / blocked
- 下一步：/ark:ark-review-gate prepare / /ark:ark-debug / /ark:ark-review-gate recheck / /ark:ark-validate
```

## 与其他 Skill 的关系

- `/ark:ark-review`：Claude Code 内部深度契约审查。用户采用跨智能体审查流程时，它不是每个 task 的必经步骤。
- 外部 Codex/其他 agent：实际执行跨智能体代码审查。
- `/ark:ark-debug`：只修复 import 后分类为“必须修复”的 findings。
- `/ark:ark-validate`：记录本地验证和外部审查 evidence，满足条件后把 Ready for validation 推进到 Done。

## 固定输出格式

```markdown
## Review Gate
- Gate 结论：
- 风险等级：
- 命中规则：
- 当前 batch：
- 是否建议继续下一个 task：
- 下一步建议：

## 外部审查材料
按当前模式输出 status / prepare / import / recheck 对应内容。

## Artifact 回写
- handoff.md：已更新 / 建议更新 / 不更新
- validation.md：不写入，建议由 /ark:ark-validate 记录
- tasks.md：不标记 Done
```

## 停止条件

- 已输出 gate 结论，或已生成外部审查包 / findings 分类 / 定向复检包。
- 已明确是否允许继续下一个 task。
- 已明确下一步应执行 `/ark:ark-debug`、`/ark:ark-review-gate recheck` 或 `/ark:ark-validate`。
