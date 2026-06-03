---
name: ark-validate
description: |
  验证当前工作是否满足目标，将验证状态记录到 docs/ark/validation.md。
  触发时机：功能实现完成后、bug 修复后、重构后、阶段交付前、准备 handoff 前。
  关键词：验证、validate、验收、检验、确认结果、测试结果记录、是否完成。
version: "1.0"
---

# /ark-validate

## 目标
验证当前工作是否满足目标，将已执行验证、建议验证、暂时无法验证的风险**严格分开**记录到 `docs/ark/validation.md`。

## 前置建议
- 建议先执行 `/ark:ark-test` 获得测试结果，再执行 `/ark:ark-validate` 记录验证状态

## 适用场景
- 功能实现完成后、bug 修复后、重构后
- 阶段交付前、准备 handoff 前

## 不适用场景
- 还没有明确产出物
- 验证目标未定义
- 当前仍处在纯规划阶段

## 职责边界

**只验证和记录，不修复。**

validate 的职责是验证实现是否满足目标，将验证状态如实记录到 `docs/ark/validation.md`，并在验证闭环时对 `docs/ark/tasks.md` 做最小状态迁移。

- **可以**：运行测试、启动服务、观察行为、执行命令、读取代码
- **不可以**：修改任何源代码文件，无论改动多小
- **仅允许的非 validation 回写**：将对应任务从 Ready for validation 迁移到 Done / Blocked，并写入 validation 记录引用或失败原因
- 一条验证记录可以覆盖多个 Ready for validation 任务，但这些任务必须属于同一功能闭环、同一 batch、同一真实入口或同一公开契约，并在 validation.md 中明确覆盖范围和覆盖原因
- 发现验证失败时，**只记录失败事实**（失败项、错误信息、复现条件），不得直接修复
- 即使是一行代码的问题（如缺少 import、拼写错误），也必须交给 `/ark:ark-debug` 处理
- 输出中必须推荐 `/ark:ark-debug` 作为修复入口

## 输入
- `/ark:ark-test` 的执行结果摘要（如有）
- 已修改代码或文档、当前任务目标、相关 Artifact
- 外部审查 evidence（如采用 `/ark:ark-review-gate`）：审查包、外部 Verdict、findings 分类、修复和复检结果
- 项目画像、真实性锚点、相关扩展文档、数据源元信息（如有）

## 相关 Artifact
- `docs/ark/validation.md`（主写入）
- `docs/ark/tasks.md`（仅允许对应任务的 Ready for validation → Done / Blocked 状态迁移）

## 验证方法优先级

验证应优先使用高保真方法，从高到低：

| 优先级 | 方法 | 强度 |
|--------|------|------|
| 1 | 真实运行环境（项目实际的启动方式 + 真实配置 + 真实依赖 / 真实数据样例） | 强 |
| 2 | 已有测试套件（pytest 等）+ 真实组件或契约边界 | 强 |
| 3 | 自定义脚本 + 真实组件（不加 mock） | 中 |
| 4 | 自定义脚本 + mock/fake/合成数据 | 弱 |

规则：
- **真实运行环境**指项目实际的启动和运行方式（从 spec.md 或 design.md 中获取）
- 对 library/CLI/frontend/data-AI/plugin，真实运行环境分别指包安装导入/命令执行/浏览器运行/真实样例数据链路/宿主加载
- **不得主动创建 mock 验证脚本**——mock 测试是 `/ark:ark-test` 的职责，不是 validate 的职责
- 如果真实环境不可用，应记入"暂时无法验证项"，**不得**降级到 mock 来凑"通过"
- 使用 mock 环境的验证结果**不得**报告为"通过"，应报告为"mock 环境通过，真实环境未验证"

## 验证保真度等级

记录验证证据时必须标注保真度：

| 等级 | 含义 |
|------|------|
| L0 | 静态检查、格式化、类型检查 |
| L1 | 单元测试，可能使用 mock/fake |
| L2 | 组件级验证，使用真实组件或真实文件格式 |
| L3 | 集成验证，使用实际配置和关键外部依赖 |
| L4 | 最小真实闭环，按项目实际入口完成核心路径 |
| L5 | 生产等价或预发布环境验证 |

mock/fake/合成数据证据最高只能证明"替身环境通过"，不能作为真实依赖或真实数据已验证的结论。

## 三类验证必须分开

### 1. 已执行验证
只记录**真实执行过**的内容：跑了哪些测试、手工验证了什么、得到了什么结果。

- 不得把「理论上没问题」写成已验证
- 不得把「准备执行的验证」写成已执行

### 2. 建议验证但未执行
应该做但当前还没做的验证，必须说明为何未执行。

### 3. 暂时无法验证的风险项
因条件不足无法完成的验证，必须说明受限原因（环境依赖、数据缺失等）。
如果真实运行环境不可用（如缺少外部服务、数据库未启动等），应记入此项，不得降级为 mock 验证来凑"通过"。

## 入口可信度检查

执行前检查 tasks.md 可信度：
- fresh → 正常执行
- stale → 提示用户"任务状态可能过期，建议先 ark-sync"
- conflicting → 停止，要求 ark-sync
- unknown → 提示并继续（刚接手项目不阻塞验证）

可信度定义见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-roles.md` 的 Artifact 可信度段。

## Sub-agent Evidence-only 模式

当 Agent tool 可用时，验证执行 spawn sub-agent：
- sub-agent 运行测试/脚本
- sub-agent **不写任何文件**
- sub-agent 返回 evidence summary（执行结果、输出、退出码）
- 主 agent 收集 summary → 写入 validation.md

当 Agent tool 不可用时，主 agent 直接执行验证，输出中记录降级说明：

```
Sub-agent 状态：未启用
原因：当前环境未提供 Agent tool
降级影响：context rot 风险较高，建议按 batch 收口，及时 handoff
```

正常启用时输出中记录：

```
Sub-agent 状态：已启用（N 个 collector）
```

sub-agent 遵循 `${CLAUDE_PLUGIN_ROOT}/rules/sub-agent-protocol.md`。

## 工作流
1. 从 `/ark:ark-test` 的输出获取已执行验证数据（如已执行）。
2. 补充手工验证、集成测试等非自动化验证结果。
3. 记录证据（命令、输出摘要、观察结果）。
4. 标注每项验证的保真度 L0-L5，并说明与项目真实性锚点的关系。
5. 对数据相关验证，只记录数据源元信息、样例范围、脱敏状态和观察结果，不记录敏感数据内容。
6. 记录未覆盖内容。
7. 记录建议验证但未执行项（说明原因）。
8. 记录暂时无法验证项（说明受限原因）。
9. 若 task 命中 external review gate，检查是否已有外部审查通过证据，或 findings 已修复并经定向复检通过。
10. 评估验证强度：弱（主要依赖手工或替身）/ 中（有自动化但真实锚点覆盖不全）/ 强（自动化覆盖主要路径 + 真实锚点或最小真实闭环）。
11. **如果发现验证失败**：记录失败项、错误信息、复现条件，不得修复代码，在输出中推荐 `/ark:ark-debug`。
12. 写入 `docs/ark/validation.md`。
13. 若验证通过且能对应到 `tasks.md` 中的 Ready for validation 项，可将对应任务迁移到 Done，并写入 validation 记录引用；多个任务共享同一验证记录时，必须确认它们同属一个功能闭环、同一 batch、同一真实入口或同一公开契约。若采用 external review gate，但外部审查证据缺失或未通过，即使本地测试通过，也必须保持 Ready for validation，并记录 `external review pending`。若验证失败，保持 Ready for validation 或转 Blocked，并记录失败事实和建议 `/ark:ark-debug`。

## 验证要求
- 严格区分事实、建议与限制
- 若验证很弱，应直接说明而不是美化
- 验证强度评估必须有依据，不得主观拔高
- **不得修改任何源代码文件**，即使改动极小（一行 import、一个拼写错误）
- 不得修改 `docs/ark/validation.md` 以外的核心 Artifact；唯一例外是对 `docs/ark/tasks.md` 中对应任务做 Ready for validation → Done / Blocked 的最小状态迁移
- 发现验证失败时，在输出中明确推荐 `/ark:ark-debug` 作为修复入口
- 当验证未通过但失败项被判断为既有问题时，必须同时记录三项：检查未通过的事实、失败项属于既有问题的判断、本次改动范围内是否发现新增问题。不得将此场景总结为"通过"
- 每条已执行验证必须标注保真度 L0-L5
- 不得把 mock/fake/in-memory/合成数据验证写成真实依赖、真实数据或最小真实闭环通过
- 数据相关验证不得写入敏感原文、密钥、连接串或大体量数据内容
- Ready for validation → Done 迁移必须有真实验证记录支撑；不得仅凭实现完成或计划验证将任务标记为 Done
- Done 任务必须引用 `validation.md` 中的具体记录；多个 Done 任务可引用同一条记录，但该记录必须列出覆盖任务、覆盖原因和未覆盖任务；验证失败时不得写成 Done
- 不得用一条宽泛验证记录覆盖无关任务；覆盖多个任务时，必须说明同一功能闭环、同一 batch、同一真实入口或同一公开契约的依据
- 若 task 已进入 external review gate，Done 还必须有外部审查 evidence：外部 review 通过，或 findings 已修复并由 `/ark:ark-review-gate recheck` 生成的定向复检通过
- 外部审查 pending 时只能记录“本地验证通过但 external review pending”，不得把任务迁移到 Done

## 停止条件
- 当前验证状态已可读、可信、可追踪
- 未覆盖项与风险已可见
- 后续验证建议已明确

## 固定输出格式

写入 `docs/ark/validation.md`：

### 1. 验证对象
### 1.5 验证覆盖范围
- 覆盖任务：
- 覆盖原因：同一功能闭环 / 同一 batch / 同一真实入口 / 同一公开契约
- 未覆盖任务：
- 不覆盖原因：
### 2. 已执行验证（附执行命令与输出摘要）
每项验证必须说明：
- 保真度：L0 / L1 / L2 / L3 / L4 / L5
- 真实性锚点：真实入口 / 真实依赖 / 真实数据源 / 公开契约 / 无直接锚点
- 替身使用：无 / mock / fake / in-memory / 合成数据（如有，说明退出条件）
### 2.5 外部审查 evidence（如适用）
- Gate 结论：
- 审查类型：single-task / batch
- 外部 Verdict：pass / needs-fix / blocked / pending
- Findings 状态：无 / 已修复并复检通过 / 仍待修复
- 覆盖任务：
- 证据来源：
### 3. 未覆盖内容
### 4. 建议验证但未执行（附原因）
### 5. 暂时无法验证项（附受限原因）
### 6. 风险结论
- 验证强度：弱 / 中 / 强（附依据）
- 当前可接受风险
- 当前不可接受风险
- 后续建议验证

### 7. 建议下一步

- 若验证强度不足且可补充测试 → `/ark:ark-test` 后再 `/ark:ark-validate`
- 若发现需要修复的问题 → `/ark:ark-debug`
- 若验证已闭环 → 将对应 Ready for validation 任务标记为 Done，并补充 `validation.md` 记录引用；多个任务共享同一记录时，确保 validation.md 明确覆盖任务和覆盖原因；如当前 Skill 未执行状态迁移，建议 `/ark:ark-tasks` 或 `/ark:ark-sync` 补齐

### 7.5 Checkpoint 建议
- 建议 checkpoint commit：是 / 否
- 建议 message：
- 建议纳入文件：
- 不建议纳入文件：

### 8. Sub-agent 状态
- Sub-agent 状态：已启用（N 个 collector）/ 未启用（原因：...）

## 备注
`/ark:ark-validate` 的价值不在于「证明一切都好」，而在于「让真实验证状态透明可见」。
验证强度弱不是失败——诚实标注才是正确做法。
