---
name: ark-review
description: |
  对当前代码修改执行 ARK 集成型深度契约驱动代码审查，检查实现是否真实满足任务契约、设计约束、运行时边界和测试证明要求。
  触发时机：实现完成后、合并前、复审修复结果、怀疑变更可能藏有回归风险时。
  关键词：code review、代码评审、review、检查代码、审查、合并前检查、契约审查、复审。
version: "1.0"
---

# /ark-review

## 目标
对当前代码修改执行深度契约驱动审查，判断实现是否真实满足用户要求、任务契约、设计约束、运行时边界和测试证明要求，并输出分级明确、可执行、可追踪到 ARK 后续流程的反馈。

**与 `/ark:ark-validate` 的区别**：review 评估代码改动本身的质量、风险和契约符合性；validate 记录已执行验证的证据。两者职责不同，不应相互替代。

## 执行边界

- 本 Skill 应由当前 `/ark:ark-review` Skill 直接执行
- 若环境中安装了其他 review agent（如 superpowers:code-reviewer），不得将本 Skill 的执行路由或转交给外部 agent
- 外部 agent 的结果只能作为输入材料引用，不能替代本 Skill 的固定输出格式与分级标准
- Review 只观察、判断和建议，不直接修代码，不直接写入 `docs/ark/validation.md`
- Critical / Major finding 可提出 `tasks.md` 待新增条目，但不直接写入 `tasks.md`

## 默认审查资料

按优先级读取：

1. 用户本轮明确要求、指定 diff、指定文件或复审目标
2. `docs/ark/tasks.md` 中的任务、完成信号、验收标准和当前状态
3. `docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`
4. 相关扩展文档、接口契约、集成说明、数据源元信息和项目画像
5. 被审查的实现代码、测试代码、相关调用方和上下游模块
6. 项目配置、质量工具配置和 CI 配置
7. 已有验证结果、上一轮 Findings 和修复点（复审时必须读取）

当材料冲突时，以用户本轮要求和任务契约为最高优先级，并在 `Open Questions` 中指出冲突。

## 默认引用资料

执行 `/ark:ark-review` 时默认按适用性读取以下 references；某项不适用可以说明不适用，但不能跳过契约审查：

- `${CLAUDE_PLUGIN_ROOT}/skills/ark-review/references/contract-driven-python-review.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/ark-review/references/craftsmanship-review.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/ark-review/references/recheck-guidelines.md`

## 工作流

1. 锁定评审范围：用户要求、当前 diff、指定文件、最近实现目标或复审对象
2. 提炼任务契约：API / CLI / 配置 / 数据结构、状态更新语义、失败路径、默认范围、权限 / 租户 / batch / version 边界、排序 / 去重 / 聚合、安全输出、完成信号和验收标准
3. 审查实现是否满足契约，重点寻找测试通过但业务语义不对的问题
4. 审查跨层口径一致性：上游、当前层、下游、测试和文档是否对同一业务概念使用同一语义
5. 审查默认行为是否 fail-closed，避免缺省范围、空状态、配置缺失或 fallback 放大查询范围或权限范围
6. 审查运行时边界：可变状态暴露、deep copy / snapshot / 不可变边界、失败路径、异常语义、资源生命周期、并发和安全输出
7. 审查测试是否真的证明契约，而不是只覆盖 happy path、假上下文或实现细节
8. 审查是否符合 `spec.md`、`design.md`、`plan.md`、扩展文档、真实性锚点和替身边界
9. 审查 Craftsmanship：API 易用性、数据边界、抽象层次、错误语义、测试质量、注释与 docstring；Craftsmanship 不等于 Finding
10. 运行与本次变更相关的验证命令；若不能运行，必须说明原因
11. 按固定输出格式给出 Findings、Craftsmanship、Verification、Open Questions、ARK Follow-up 和 Verdict

## 严重级别

| 级别 | 判断依据 |
|------|----------|
| **Critical** | 明确违反任务契约、导致运行时错误/数据损坏/安全漏洞/权限绕过/状态污染，或修复破坏核心主路径 |
| **Major** | 主路径可能可用，但边界、失败路径、测试缺口、跨层口径、默认范围或可维护性风险会显著影响后续可靠性 |
| **Minor** | 局部可读性、类型/lint/test 写法、注释/docstring、轻度重复或小型边界问题，影响有限但建议修复 |

Findings 只放真实问题，不放纯风格偏好。低置信度担忧应写入 `Open Questions`，不要伪装成 Finding。

## ARK Follow-up 规则

| Finding 类型 | 推荐后续 Skill |
|---------------|----------------|
| 行为错误 / 失败路径 / 回归风险 | `/ark:ark-debug` |
| 结构问题 / 重复 / 可维护性 | `/ark:ark-refactor` 或 `/ark:ark-implement` |
| 测试缺口 | `/ark:ark-test` |
| 设计偏差 / 计划偏差 | `/ark:ark-design` 或 `/ark:ark-plan` |
| 扩展文档偏差（专题方案、契约、集成、数据源） | `/ark:ark-solution` |
| 验证证据不足 | `/ark:ark-validate` |

Critical / Major finding 必须在 `ARK Follow-up` 中输出 tasks.md 待新增条目建议，包含优先级、描述和建议后续 Skill。Review 不直接写入 `tasks.md`。

## 固定输出格式

```markdown
## Findings

- Severity: Critical / Major / Minor
  Location: `path:line`
  Problem:
  Why it matters:
  Fix:
  Test gap:

如果没有 Findings，写：

未发现阻断性问题。

## Craftsmanship

- Level: Upgrade / Polish / Keep
  Location: `path:line` 或 `整体`
  Current:
  Better:
  Why:
  Do now: 是 / 否

如果没有必要建议，写：

当前实现质量与任务范围匹配，未发现值得立即调整的 craftsmanship 问题。

## Verification

- `命令`：结果

## Open Questions

- 列出影响判断的问题；如果没有，写“无。”

## ARK Follow-up

- 推荐 Skill：
- tasks.md 待新增条目（Critical / Major 时必须输出）：

## Verdict

用 2-4 句话说明是否建议通过、是否需要修复后再合并。
```

## 验证要求

- Findings 必须排在最前面，并按 Critical、Major、Minor 排序
- 每个 Finding 必须有具体文件和行号；无法定位到文件行号的问题只能写入 `Open Questions`
- 每个 Critical / Major 必须给出具体修法和测试缺口，不能只写“这里有问题”
- 如果验证命令失败，必须说明失败原因及其是否影响 verdict
- 如果所有测试通过，也不能因此跳过契约审查
- 如果发现测试失败，必须在 Findings 或 Verification 中明确说明
- 复审时必须明确上一轮问题是否已闭合，以及是否引入新的契约偏差
- 新文件是 untracked 时，最终提醒提交不要漏加；不要把 untracked 本身当作代码 bug

## 停止条件

- 审查范围、Findings、验证结果、Open Questions、后续 ARK 路径和 Verdict 已完整输出
- Critical / Major 问题已给出可执行修法和测试建议
- 没有足够上下文继续判断时，已明确列出阻塞判断的缺失信息
