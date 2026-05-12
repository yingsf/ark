---
name: ark-implement
description: |
  依据 spec、design、plan 和真实仓库状态，完成最小可行实现，必要时回写相关 Artifact。
  触发时机：已具备足够清晰的实现目标、需要将计划落地为代码、已知问题需要修复时。
  关键词：实现、编码、写代码、implement、开发、落地、执行计划。
version: "1.0"
---

# /ark-implement

## 目标
依据当前 spec、design、plan 和真实仓库状态，完成最小可行实现，并在必要时回写相关 Artifact。

## 适用场景
- 已具备足够清晰的实现目标
- 需要将计划中的某一步落地为代码
- 已知问题需要具体修复
- 需要逐步推进一个中大型任务

## 不适用场景
- 目标仍存在关键歧义
- 设计或边界不明确，贸然实现风险过高
- 当前更需要先做 review、sync 或 validate

## 前置建议

| 情况 | 建议命令 |
|------|----------|
| 目标不明确 | `/ark:ark-intake` |
| 需求未规格化 | `/ark:ark-spec` |
| 无执行计划 | `/ark:ark-plan` |
| 文档可能过期 | `/ark:ark-sync` |

## 输入
- 当前相关代码、`docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`、`docs/ark/tasks.md`

## 输出
- 已完成的代码修改
- 对假设、限制、延期项的说明
- 必要时对 plan / tasks / decisions 的回写
- 对后续 test / validate 的建议

## 相关 Artifact
- 可读取：`docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`、`docs/ark/tasks.md`
- 可在必要时回写：`docs/ark/plan.md`、`docs/ark/tasks.md`
- 若出现关键取舍，应建议更新：`docs/ark/decisions.md`

## 工作流

### Small 任务
1. 确认目标（单点修改）。
2. 完成修改，保持最小改动范围。
3. 在修改完成点执行局部质量整理（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行）；若工具修改了文件，重新读取当前内容或 diff。
4. 完成后建议 `/ark:ark-test` 和 `/ark:ark-validate`。

### Medium / Large 任务
1. 读取相关代码和 Artifact，确认当前 plan 状态有效。
2. 明确本次只完成哪一步，不默认顺手扩展范围。
3. **批次评估**：若出现批次触发信号（见下方「批次实施机制」），拆分为实施批次并只完成当前批次。否则正常执行。
4. 选择最小可行修改：小步推进、局部修改、可验证、可回退。每个批次内的修改应构成一个相对完整的子问题。
5. 避免混入无关改动（风格清理、无关重命名、大面积重构）。
6. **批次执行**：每完成一个批次后，在稳定点执行局部质量整理（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行），输出批次完成状态，更新 tasks.md 记录批次进展。然后建议下一批次或停止。
7. 实施后检查是否需要回写 Artifact（见下方回写规则）。
8. 若当前会话需要中断，优先完成当前批次再执行 `/ark:ark-handoff`。若处于批次中间且无法完成，handoff 应记录当前批次进展。
9. 完成后建议 `/ark:ark-test` 和 `/ark:ark-validate`。

## 批次实施机制

本节适用于 Medium / Large 任务中修改范围较大的场景。

### 触发信号

出现以下任一信号时，应优先考虑批次实施：

- 涉及 3 个以上文件
- 单文件大段重写（非增删个别函数）
- 存在明显顺序依赖（必须先完成 A 才能做 B）
- 预期单次修改难以在一个稳定回合内完成

### 硬约束

- 触发批次信号时，**不得**默认一次完成全部修改；应先拆成实施批次，并只完成当前批次

### 批次四要素

每个实施批次应明确定义：

| 要素 | 含义 |
|------|------|
| 本批目标 | 这一 batch 要达成什么 |
| 涉及文件 | 本批改动哪些文件 |
| 修改锚点 | 每个文件中改哪一段 / 哪一类调用点 |
| 完成信号 | 这一 batch 什么时候算做完 |

### 执行规则

- 每次只执行一个批次
- 每个批次结束后执行局部质量整理和检查（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行）
- ruff lint fix 只在批次完成、当前修改已处于稳定点时执行；编辑中的 PostToolUse hook 只负责 format，不负责 lint fix
- 若 ruff check --fix 修改了文件，必须重新读取受影响文件或 diff，再继续判断任务状态
- 更新 `docs/ark/tasks.md` 记录批次进展（在任务备注区记录当前批次）
- 输出当前批次完成状态，建议下一批次或停止

### Sub-agent Batch 模式

Medium/Large 任务可启用 batch sub-agent 模式缓解 context rot：

1. **检查 Agent tool 是否可用**
   - 可用：每个 batch spawn 独立 sub-agent
   - 不可用：单上下文顺序执行，输出降级说明

2. **sub-agent 遵循** `${CLAUDE_PLUGIN_ROOT}/rules/sub-agent-protocol.md`
   - 只写 batch write set 内的源文件
   - 不写 docs/ark/*

3. **Write Set 审计**
   - 执行前：主 agent 记录 batch write set（本批声明要修改的文件列表）
   - 执行后：检查 diff 是否超出 write set
   - 越界 → 停止并报告，列出意外修改的文件，不自动合并
   - 正常 → 复核通过后主 agent 更新 Artifact

4. **batch 完成后主 agent**：
   - 复核 diff
   - 对已改 Python 文件运行 ruff check --fix + ruff format（如可用），并在其修改文件后重新复核 diff
   - 运行 pyright（如可用）
   - 更新 tasks.md
   - 进入 Git Checkpoint 流程

5. **降级输出**

   Agent tool 不可用时：
   ```
   Sub-agent 状态：未启用
   原因：当前环境未提供 Agent tool
   降级影响：context rot 风险较高，建议按 batch 收口，及时 handoff
   ```

   正常启用时：
   ```
   Sub-agent 状态：已启用（N 个 worker）
   ```

### 中断安全

- 批次完成点是天然的中断安全点——当前批次所有文件修改已落盘、局部检查已执行、已知未完成内容已列清
- 若未到达批次完成点且会话即将中断，优先完成当前批次再 handoff
- 若确实无法完成当前批次，handoff 必须记录：已完成的文件/锚点、未完成的文件/锚点、下一批次入口

### 回写 `docs/ark/plan.md`
- 实际步骤与原计划明显不同
- 风险或阻塞发生重大变化
- 执行顺序需要调整

### 回写 `docs/ark/tasks.md`
- 某任务已完成 → 移入 Done
- 某任务已开始 → 移入 Doing
- 出现新阻塞 → 加入 Blocked（附解除条件）

### 建议更新 `docs/ark/decisions.md`
- 做出了非平凡技术取舍或选用了新的实现路线

## Deviation Handling

实施中发现的问题按以下规则处理：

| 发现类型 | 处理方式 | 记录到 |
|---------|---------|--------|
| 当前 batch 范围内的 bug | 自动修复 | tasks.md |
| 阻塞当前 batch，不改架构 | 自动处理或标记 Blocked | tasks.md |
| 需要改变阶段顺序 | 更新执行顺序 | plan.md |
| 需要改变架构或不可逆取舍 | 停止，推荐 ark-decide | — |
| 无关但值得注意 | 记录风险 | handoff.md risks 段 |

## Git Checkpoint

每个 batch 完成后，根据任务大小决定 checkpoint 条件：

- **Small 任务**：batch 完成 → 可选 checkpoint commit
- **Medium/Large 任务**：batch 完成 → 相关 test 子集通过 → validate evidence 草稿可用 → 建议 checkpoint commit

commit 范围：该 batch 修改的文件
commit 格式：`<type>(<scope>): <batch-goal>`
不自动提交，等用户确认

## 验证要求
- 实现内容应与已定义目标一致
- 任何额外扩 scope 都应显式指出
- 改动后的行为应具备验证路径
- 若执行 ruff / pyright / pytest 等检查命令返回非 0，不得表述为"pass / 通过"。若失败项被判断为既有问题，应写"检查未通过，但未发现本次改动新增问题"。最终验证结论应交由 `/ark:ark-validate` 记录
- 在不扩大 scope 的前提下，新增或修改的公共接口应补充清晰 docstring；复杂、关键、非直观或涉及降级/资源/并发边界的逻辑，应补充必要中文注释。注释以清晰、克制、服务维护为原则，不做无关文档化扩展
- 触发批次信号时，不得跳过批次拆分直接一次性完成全部修改
- 不得为了对抗 format hook 而把原本可小步完成的修改扩大为整文件重写；如果 hook 在编辑后改动了文件，应先重新读取当前内容或 diff，再继续做最小修改
- 实现代码应遵循 python-backend-conventions.md 中的可维护性规范：避免高复杂度函数（多层分支/嵌套判断应拆分辅助函数）、优先使用公开接口（不直接访问 protected 成员）、主动识别并处理大段重复代码。对中大型、分批实施的任务，还应评估当前批次与前序批次是否形成跨文件重复；若当前不适合立即抽取，必须将去重整理显式记录为后续收口任务。当快速实现会明显增加结构债时，应优先做小范围重构，而非留到 review 才处理

## 停止条件
- 当前目标的代码修改已完成，可以进入测试或验证
- 或已明确指出为何当前不适合继续实现
- 或会话中断，已执行 `/ark:ark-handoff`

## 固定输出格式

### 1. 本次实现目标
### 2. 主要修改（文件 + 变更摘要）
### 2.5 批次进展（批次实施时）
- 当前批次：Batch n/m
- 本批目标：
- 已修改文件与锚点：
- 本批完成信号 / 未完成项：
### 3. 假设 / 限制 / 延期项
### 4. Artifact 回写
### 5. 建议下一步

- 若本次修改涉及可测试逻辑（新增/修改的公共方法、条件分支、错误处理）→ `/ark:ark-test` → `/ark:ark-validate`
- 若本次修改不涉及可测试逻辑（纯配置、文档、样式）→ `/ark:ark-validate`
- 若会话即将中断 → `/ark:ark-handoff`

### 6. Sub-agent 状态
- Sub-agent 状态：已启用（N 个 worker）/ 未启用（原因：...）

## 备注
`/ark:ark-implement` 的目标不是「尽可能多写代码」，而是「以最低风险推进真实进展」。

PostToolUse ruff hook 只做格式化，不做 lint auto-fix。lint auto-fix 由 implement 在批次完成等稳定点执行，避免编辑中间态被删除未使用导入等自动修复干扰。

若非 Python 文件编辑与项目 formatter / hook 存在冲突，应优先将其视为工具链问题；在当前约束下若必须采用替代写入方式，应明确说明原因，且不得把绕过 hook 当成默认实现路径。
