---
name: ark-implement
description: |
  依据 spec、design、plan 和真实仓库状态，完成最小可行实现，并按边界更新执行状态。
  触发时机：已具备足够清晰的实现目标、需要将计划落地为代码、已知问题需要修复时。
  关键词：实现、编码、写代码、implement、开发、落地、执行计划。
version: "1.0"
---

# /ark-implement

## 目标
依据当前 spec、design、plan 和真实仓库状态，完成最小可行实现，并按边界更新允许的执行状态 Artifact。

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
- 当前相关代码、`docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`、`docs/ark/tasks.md`、`docs/ark/validation.md`、`docs/ark/handoff.md`、`docs/ark/decisions.md`
- 项目画像、真实性锚点、相关扩展文档（如有）

## 输出
- 已完成的代码修改
- 功能结果报告：本次新增/改变的能力、触发方式、可观察结果、限制和与原目标的对应关系
- 外部审查门禁建议：immediate / batch-candidate / batch-ready / blocked
- 对假设、限制、延期项的说明
- 必要时对 plan / tasks / decisions 的回写
- 对后续 test / validate 的建议

## 相关 Artifact
- 可读取：`docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`、`docs/ark/tasks.md`、`docs/ark/validation.md`、`docs/ark/handoff.md`、`docs/ark/decisions.md`
- 可在必要时回写：`docs/ark/plan.md`、`docs/ark/tasks.md`
- 若出现关键取舍，应建议更新：`docs/ark/decisions.md`
- 若本次实现改变规格或设计现实，应建议 `/ark:ark-spec` 或 `/ark:ark-design`；不得直接回写 `docs/ark/spec.md` 或 `docs/ark/design.md`
- 若本次实现改变专题方案、详细设计、接口契约、集成或数据源元信息，应建议 `/ark:ark-solution`；不得直接回写扩展文档

## 工作流

### 执行目标锁定

编码前必须先锁定本轮唯一执行目标，避免把 `tasks.md` 中多个 Todo 自动合并为一次实现。

目标选择优先级：

1. 用户明确指定的 task、文件、修复目标或 batch
2. `tasks.md` 中唯一 `Doing` 项
3. 第一个依赖已满足、未阻塞、最高优先级的 `Todo` 项
4. 若无法唯一判断，停止并建议 `/ark:ark-next`，或请用户明确本轮目标

锁定后必须在输出中声明：

```text
本轮唯一执行目标：T{id} {任务名} / Batch n/m {批次名}
选择理由：用户指定 / 唯一 Doing / 第一个可执行 Todo / 明确 batch
本轮不处理：T...（说明不会自动继续的任务）
```

未指定多个任务或阶段批次时，不得连续执行多个 Todo，不得完成当前任务后自动进入下一个任务，不得把 plan 或 tasks 中的全部任务当成本轮目标。

### 显式功能 Batch 例外

默认仍只推进一个 task 或一个已声明 batch。只有用户明确要求、`tasks.md` 已记录当前批次，或 plan 明确把多个 task 作为同一实施批次时，才允许一次覆盖多个 task。

允许合并的条件：

- 多个 task 属于同一个功能交付单元、技术闭环、真实入口或公开契约
- 多个 task 需要一起实现后才具备可观察结果
- 可以用同一组测试或同一条 validation 记录合理覆盖
- 合并后仍能明确停止边界，不会顺手执行后续无关 task

禁止合并的情况：

- 只是因为都排在 Todo 前面
- 只是为了减少流程步骤，但功能、入口或验证证据无关
- 某个 task 存在未满足依赖或 Blocked，且未先处理依赖
- 合并会把验证记录变成宽泛的“都看过了”

执行显式 batch 前必须声明：

```text
本轮执行类型：功能 batch
覆盖任务：T...
合并原因：同一功能交付单元 / 同一技术闭环 / 同一真实入口 / 同一公开契约
统一验证计划：将如何用一组测试或一条 validation 记录覆盖
停止边界：不处理 T...
```

### Small 任务
1. 确认本轮唯一执行目标（单点修改）。
2. 读取并吸收相关 `validation.md` 未覆盖项、`handoff.md` 恢复提示、`decisions.md` 约束；若存在与当前目标冲突的前序结论，先停止并建议 `/ark:ark-sync`。
3. 执行 Reality Check：确认本次是否涉及真实入口、真实依赖、真实数据源或公开契约；若不涉及，说明原因。
4. 观察同模块或相邻模块的注释/docstring 风格；若项目风格不明确，使用 ARK 默认 `fastchain-enhanced` 中文 Google 风格。
5. 完成修改，保持最小改动范围，并同步补齐必要 docstring 和中文注释。
6. 在修改完成点执行局部质量整理（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行）；若工具修改了文件，重新读取当前内容或 diff。
7. 检查新增/修改的公共接口、关键方法和复杂逻辑是否符合注释/docstring 要求。
8. 输出功能结果：先说明新增/改变的能力、触发方式、可观察结果、限制和与原目标的对应关系，再说明文件修改。
9. 执行 External Review Gate 轻量评估：按 `${CLAUDE_PLUGIN_ROOT}/rules/external-review-gate.md` 判断当前 task 是 `immediate`、`batch-candidate`、`batch-ready` 还是 `blocked`。
10. 执行 spec/design/extension 漂移检查：只识别本次实现是否改变需求、设计现实或扩展文档现实，发现后在输出中建议对应 Skill，不直接回写 spec/design 或扩展文档。
11. 若实现完成但尚未验证，tasks.md 只能更新为 Ready for validation，不得标记 Done。
12. 完成当前目标后停止，若 gate 为 `immediate` 或 `batch-ready`，优先建议 `/ark:ark-review-gate prepare`；若 gate 为 `batch-candidate`，说明可继续下一个同闭环低风险 task；否则建议 `/ark:ark-test` 和 `/ark:ark-validate`。

### Medium / Large 任务
1. 读取相关代码和 Artifact，确认当前 plan/tasks/validation/handoff 状态有效。
2. 吸收前序结论：读取相关 validation 未覆盖项、handoff 恢复提示、decisions 约束、相关扩展文档；明确本次处理哪些、不处理哪些及原因。
3. 锁定本轮唯一执行目标：用户指定目标、唯一 Doing、或第一个依赖已满足的最高优先级 Todo；不得默认连续执行多个 Todo。
4. 若目标任务存在未完成依赖，不得跳过依赖直接实现；应先选择最小未完成依赖作为本轮目标，或停止并建议 `/ark:ark-tasks` / `/ark:ark-plan` 校准依赖。
5. 执行 Reality Check：读取项目画像、plan/tasks 中的真实性锚点和相关扩展文档，确认本批次如何推进真实闭环。
6. 若 tasks 已推进很多但真实入口、真实依赖、真实数据源或公开契约仍缺失，先停止并建议 `/ark:ark-sync` 或 `/ark:ark-plan` 重新校准，不继续堆叠占位实现。
7. 观察同模块或相邻模块的注释/docstring 风格；若项目风格不明确，使用 ARK 默认 `fastchain-enhanced` 中文 Google 风格。
8. 明确本次只完成哪一步，不默认顺手扩展范围。
9. **批次评估**：若出现批次触发信号（见下方「批次实施机制」），拆分为实施批次并只完成当前批次。否则正常执行。
10. 选择最小可行修改：小步推进、局部修改、可验证、可回退。每个批次内的修改应构成一个相对完整的子问题，并尽量靠近最小真实闭环。
11. 避免混入无关改动（风格清理、无关重命名、大面积重构）。
12. **批次执行**：每完成一个批次后，在稳定点执行局部质量整理（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行），检查新增/修改的公共接口、关键方法和复杂逻辑是否符合注释/docstring 要求，输出功能结果，执行 External Review Gate 轻量评估，执行 spec/design/extension 漂移检查，输出批次完成状态，更新 tasks.md 记录批次进展。然后按 gate 结论建议外部审查、继续同闭环低风险 task 或停止。
13. 实施后检查是否需要回写 Artifact（见下方回写规则）。
14. 若当前会话需要中断，优先完成当前批次再执行 `/ark:ark-handoff`。若处于批次中间且无法完成，handoff 应记录当前批次进展。
15. 完成当前目标后停止，建议 `/ark:ark-test` 和 `/ark:ark-validate`；如需继续下一个任务，请用户再次执行 `/ark:ark-implement`。

## Reality Check

每次实现开始前必须做轻量 Reality Check：

1. 判断项目类型：backend service / library SDK / CLI / frontend / data-AI / plugin / mixed / unknown。
2. 找出本次任务的真实性锚点：
   - backend：启动入口、配置加载、数据库/搜索/队列/第三方 API、HTTP/MCP/API 调用
   - library：安装、导入、公开 API、协议行为
   - CLI：真实命令、参数、文件输入、退出码、stdout/stderr
   - frontend：浏览器运行、关键交互、接口调用
   - data-AI：真实样例数据路径元信息、文件格式、解析/编译/评估链路
   - plugin：宿主加载、生命周期钩子、配置边界
3. 判断本批次是推进真实锚点、使用替身、还是纯内部整理。
4. 若使用 mock/fake/in-memory/合成数据，必须说明替身边界和退出条件。
5. 若缺少必要真实依赖、数据源或契约文档，先建议 `/ark:ark-solution`、`/ark:ark-plan` 或 `/ark:ark-sync`，不得把替身实现当作真实完成。

## 批次实施机制

Medium/Large 任务、显式功能 Batch、触发批次信号或使用 sub-agent 时，读取 `${CLAUDE_PLUGIN_ROOT}/skills/ark-implement/references/batch-subagent-guidelines.md`。

核心摘要：

- 涉及 3 个以上文件、单文件大段重写、明显顺序依赖或单次难以稳定完成时，应优先拆成 batch
- 未指定 task、batch 或阶段范围时，不得连续执行多个 Todo
- 覆盖多个 task 的 batch 必须声明覆盖任务、合并原因、统一验证计划和批次边界
- sub-agent 只能写 batch write set 内的源文件，越界必须停止并报告
- Checkpoint 建议只在 batch 完成、稳定提交点或用户要求时输出

## 注释与 docstring 执行规则

新增/实质修改公共接口、关键方法、复杂逻辑、资源生命周期、并发/降级/失败处理时，读取 `${CLAUDE_PLUGIN_ROOT}/skills/ark-implement/references/comment-docstring-guidelines.md`。

核心摘要：

- 修改前观察 `CLAUDE.md` 和相邻代码风格；无明确约定时使用 `fastchain-enhanced` 中文 Google 风格
- 实现前判断注释详细度分级：L0 / L1 / L2 / L3
- 默认不主动新增顶部模块级 docstring，不使用变量后置三引号
- 中文 docstring / 中文注释不使用句末中文终止标点，不写业务解释型尾随注释
- 公共接口、关键方法、复杂逻辑和资源生命周期边界必须补充必要说明

### 回写 `docs/ark/plan.md`
- 实际步骤与原计划明显不同
- 风险或阻塞发生重大变化
- 执行顺序需要调整

### 回写 `docs/ark/tasks.md`
- 某任务已开始 → 移入 Doing
- 某任务实现已完成但未验证 → 移入 Ready for validation
- 某任务已完成且已有 validation.md 验证记录 → 可移入 Done（通常由 `/ark:ark-validate` 触发）
- 出现新阻塞 → 加入 Blocked（附解除条件）
- 状态迁移必须是移动而不是复制；同一个 task ID 不得跨状态重复出现
- 回写后必须自检 task ID 唯一性；若发现重复或无法安全迁移，停止并建议 `/ark:ark-sync`
- 不得为未纳入本轮唯一执行目标或当前批次边界的 task 更新状态

日期要求：
- 回写 `docs/ark/tasks.md` 时，只更新真实发生变化的任务状态、批次备注或阻塞信息
- 如内容被修改，头部 `last-updated` 使用当前会话真实日期
- 同一天多次 implement 不得递增日期，不得写入未来日期

### 建议更新 `docs/ark/decisions.md`
- 做出了非平凡技术取舍或选用了新的实现路线

### 建议更新 `docs/ark/spec.md`
只建议，不直接回写。出现以下任一情况时，输出中推荐 `/ark:ark-spec`：
- 本次实现新增、删除或改变用户可感知能力
- 能力范围、非目标、验收标准或成功条件发生变化
- 外部接口、MCP/API 契约、导入导出能力、权限或数据可见范围发生变化
- 实现结果与 `spec.md` 中的能力承诺、范围或验收描述不一致

### 建议更新 `docs/ark/design.md`
只建议，不直接回写。出现以下任一情况时，输出中推荐 `/ark:ark-design`：
- 模块边界、职责划分、调用链、数据流或依赖方向发生变化
- 新增或替换核心抽象、运行时组件、服务层、仓储层、适配器或外部系统集成方式
- 接口契约、资源生命周期、并发/限流/缓存/降级策略发生变化
- 实现路线与 `design.md` 的既有方案明显不同，但不一定达到 decisions.md 的不可逆决策标准

### 建议更新扩展文档
只建议，不直接回写。出现以下任一情况时，输出中推荐 `/ark:ark-solution`：
- 专题方案、详细设计、接口契约、集成方式或数据源元信息与实现不一致
- 新增或改变 HTTP/MCP/API/CLI/SDK/文件格式/事件契约的细节，需要扩展文档承载
- 替身边界、真实数据样例范围、外部系统失败语义或接入方式发生变化
- 实现发现缺少必要 solution/design/contracts/data-sources 文档，导致后续 plan/tasks 难以继续

## Deviation Handling

实施中发现的问题按以下规则处理：

| 发现类型 | 处理方式 | 记录到 |
|---------|---------|--------|
| 当前 batch 范围内的 bug | 自动修复 | tasks.md |
| 阻塞当前 batch，不改架构 | 自动处理或标记 Blocked | tasks.md |
| 需要改变阶段顺序 | 更新执行顺序 | plan.md |
| 需求范围、验收标准或能力承诺变化 | 建议 ark-spec | — |
| 模块边界、接口契约或运行机制变化 | 建议 ark-design | — |
| 专题方案、契约、集成、数据源元信息或替身边界变化 | 建议 ark-solution | — |
| 需要改变架构或不可逆取舍 | 停止，推荐 ark-decide | — |
| 无关但值得注意 | 记录风险 | handoff.md risks 段 |

## Git Checkpoint

Checkpoint 细则见 `${CLAUDE_PLUGIN_ROOT}/skills/ark-implement/references/batch-subagent-guidelines.md`。

默认不自动提交。仅在 Medium/Large、明确 batch 完成、用户要求提交或存在稳定提交点时输出 Checkpoint 建议，并等待用户确认。

## 验证要求
- 实现内容应与已定义目标一致
- 任何额外扩 scope 都应显式指出
- 默认输出必须包含功能结果，并位于文件级修改摘要之前
- 功能结果必须说明当前完成状态、任务状态建议、本次新增/改变的能力、用户或调用方如何触发、可观察结果、不包含什么、当前限制、用户验收方式以及与原目标的对应关系
- 若本次无直接用户可见功能变化，必须明确写明，并说明它支撑的内部能力或间接价值
- 若实现结果与原目标存在偏差，必须先在功能结果中说明，不得只放在限制项或 Artifact 回写中
- 默认报告只输出影响用户判断、验收和下一步行动的内容；过程细节按条件输出
- 默认输出必须包含外部审查门禁，说明 Gate 结论、风险等级、命中规则、当前 batch、是否建议继续下一个 task 和下一步建议
- Gate 结论为 `immediate` 或 `batch-ready` 时，不应建议继续下一个 task，应建议 `/ark:ark-review-gate prepare`
- Gate 结论为 `batch-candidate` 时，只能建议继续同一功能闭环内的低风险 task，且最多遵守 3 个 task / 90 分钟 / 1 个功能闭环 / 500 行核心 diff 的上限
- Sub-agent 状态仅在已启用、失败、降级或影响可信度时输出
- 注释与 docstring 详情仅在新增/修改对象需要说明、存在例外、未满足要求或用户关注代码规范时输出
- Reality Check 详情仅在涉及真实依赖、真实数据源、替身边界、契约风险或可信度变化时输出；普通场景压缩到验证状态或风险与回写中
- Checkpoint 建议仅在 Medium/Large、明确 batch 完成、用户要求提交或存在稳定提交点时输出
- `tasks.md` task ID 唯一性仅在本次更新 `tasks.md` 或发现异常时输出
- 改动后的行为应具备验证路径
- 实现完成但未执行 `/ark:ark-validate` 或没有对应验证记录时，不得将 tasks.md 任务标记为 Done；最多进入 Ready for validation
- 显式功能 batch 可将多个强相关 task 一起推进到 Ready for validation，但必须记录覆盖任务、合并原因、统一验证计划和停止边界
- 必须在输出中说明前序结论吸收情况，包括 validation 未覆盖项、handoff 恢复提示、decisions 约束和本次未处理原因
- 若执行 ruff / pyright / pytest 等检查命令返回非 0，不得表述为"pass / 通过"。若失败项被判断为既有问题，应写"检查未通过，但未发现本次改动新增问题"。最终验证结论应交由 `/ark:ark-validate` 记录
- 编码前必须锁定本轮唯一执行目标；未指定 task、batch 或阶段范围时，不得连续执行多个 Todo，不得完成当前目标后自动进入下一个任务
- 若当前目标存在未完成依赖，不得跳过依赖实现后续 task；应先处理最小未完成依赖，或建议 `/ark:ark-tasks` / `/ark:ark-plan`
- 在不扩大 scope 的前提下，新增或修改的公共接口应补充中文 Google 风格 docstring；复杂、关键、非直观或涉及降级/资源/并发边界的逻辑，应补充必要中文注释。注释以清晰、克制、服务维护为原则，不做无关文档化扩展
- 新增/修改对象必须先判断注释等级 L0/L1/L2/L3；L2/L3 对象应使用 fastchain-enhanced 增强 docstring，L0 对象不得为了形式补低价值注释
- 新建或修改 Python 文件时，不主动新增顶部模块级 docstring；不得使用变量后置三引号 / attribute docstring 解释常量、变量、集合或配置项
- 中文 docstring 和中文注释不得使用句末中文终止标点；业务解释类注释应写在代码上方，不写尾随解释注释
- 若新增/修改公共接口、关键方法或复杂逻辑后缺少必要 docstring/注释，不得将本次实现视为完整完成；应在当前 scope 内补齐，或明确说明为何项目既有风格不要求补充
- 每个完成点必须执行 spec/design 漂移检查。发现漂移时只能建议 `/ark:ark-spec` 或 `/ark:ark-design`，不得直接修改 `docs/ark/spec.md` 或 `docs/ark/design.md`
- 每个完成点必须执行扩展文档漂移检查。发现漂移时只能建议 `/ark:ark-solution`，不得直接修改扩展文档
- 不得把 mock/fake/in-memory/合成数据实现报告为真实依赖或真实数据已接入；必须标注替身边界和退出条件
- 对与真实基础设施、真实数据或公开契约强相关的任务，若长期无法推进真实锚点，应停止并建议重新规划，而不是继续堆叠占位代码
- 触发批次信号时，不得跳过批次拆分直接一次性完成全部修改
- 完成当前目标后停止，输出下一步建议；如需继续实现下一个任务，应由用户再次触发 `/ark:ark-implement`
- 回写 tasks.md 后必须确认同一个 task ID 未跨状态重复出现
- 不得为了对抗 format hook 而把原本可小步完成的修改扩大为整文件重写；如果 hook 在编辑后改动了文件，应先重新读取当前内容或 diff，再继续做最小修改
- 实现代码应遵循 python-backend-conventions.md 中的可维护性规范：避免高复杂度函数（多层分支/嵌套判断应拆分辅助函数）、优先使用公开接口（不直接访问 protected 成员）、主动识别并处理大段重复代码。对中大型、分批实施的任务，还应评估当前批次与前序批次是否形成跨文件重复；若当前不适合立即抽取，必须将去重整理显式记录为后续收口任务。当快速实现会明显增加结构债时，应优先做小范围重构，而非留到 review 才处理

## 停止条件
- 当前目标的代码修改已完成，可以进入测试或验证
- 或已明确指出为何当前不适合继续实现
- 或会话中断，已执行 `/ark:ark-handoff`

## 固定输出格式

### 1. 功能结果
- 当前完成状态：实现完成 / 部分完成 / 阻塞 / 需要确认
- 任务状态建议：Ready for validation / Blocked / 不更新 tasks
- 本次新增 / 改变的能力：
- 用户或调用方如何触发：
- 可观察结果：
- 不包含什么 / 当前限制：
- 用户验收方式：运行命令 / 打开页面 / 调用接口 / 观察结果
- 与原目标的对应关系：

### 2. 实现摘要
- 本轮目标：
- 选择理由：
- 主要修改：
- 本轮不处理：
- 前序结论吸收：validation 未覆盖项 / handoff 恢复提示 / decisions 约束 / 本次未处理原因

### 3. 验证状态
- 已执行检查：
- 未执行验证：
- 真实锚点 / 替身边界摘要：
- 建议下一步：

### 4. 外部审查门禁
- Gate 结论：immediate / batch-candidate / batch-ready / blocked
- 风险等级：High / Medium / Low
- 命中规则：
- 当前 batch：
- 是否建议继续下一个 task：
- 下一步建议：

### 5. 风险与回写
- 假设 / 限制 / 延期项：
- Artifact 回写：
- 需要更新 spec/design/decisions/扩展文档：

## 条件输出

以下章节仅在对应条件成立时输出，不作为每次默认报告的固定噪音：

### Batch 进展
- 当前批次：Batch n/m
- 本批目标：
- 覆盖任务：
- 合并原因：
- 统一验证计划：
- 批次边界：
- 已修改文件与锚点：
- 本批完成信号 / 未完成项：

### Reality Check 详情
- 项目类型：
- 本次真实性锚点：
- 真实依赖 / 数据源 / 契约状态：
- 替身边界与退出条件：

### 注释与 docstring 详情
- 注释详细度判定：L0 / L1 / L2 / L3
- 已补充说明：
- 例外或未补充原因：

### Checkpoint 建议
- 建议 checkpoint commit：是 / 否
- 建议 message：
- 建议纳入文件：
- 不建议纳入文件：

### Sub-agent 状态
- Sub-agent 状态：已启用（N 个 worker）/ 未启用（原因：...）

## 备注
`/ark:ark-implement` 的目标不是「尽可能多写代码」，而是「以最低风险推进真实进展」。

PostToolUse ruff hook 只做格式化，不做 lint auto-fix。lint auto-fix 由 implement 在批次完成等稳定点执行，避免编辑中间态被删除未使用导入等自动修复干扰。

若非 Python 文件编辑与项目 formatter / hook 存在冲突，应优先将其视为工具链问题；在当前约束下若必须采用替代写入方式，应明确说明原因，且不得把绕过 hook 当成默认实现路径。
