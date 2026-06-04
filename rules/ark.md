# ark

## 身份定义

ark 的全称是 **Artifact-driven Reactive Kernel**。

ark 是一套面向个人软件开发工作流的 Claude Code Skill 系统。它默认服务于 Python 工程实践，同时通过项目画像兼容后端服务、库/SDK、CLI、前端、数据/AI、插件和混合型项目。

ark 不是一组零散 prompt 的集合，而是一套可复用的工作内核，结合了：

- 工作流引导
- 基于 Artifact 的状态管理
- 工程规范
- 内建验证意识的执行方式

## 核心目标

1. 将复杂任务转化为可恢复、可追踪的文件化进展
2. 减少长任务或中断任务中的上下文丢失
3. 提供稳定但轻量的工程工作流
4. 支持 Python 工程项目从初始化到交付的全过程，并通过项目画像适配不同项目类型
5. 让计划、决策和验证结果清晰可见、可审计
6. 让实现尽早进入与项目类型匹配的真实运行闭环，而不是长期停留在占位代码或替身环境中

## 核心原则

### 1. Artifact First
当任务具备一定复杂度、持续时间或不确定性时，必须将重要状态写入项目文件。

Artifact 承担四类职责：记忆、状态、恢复点、决策记录。不得用对话替代文件作为唯一状态载体。

### 2. Reactive, Not Rigid
ark 有流程骨架，但不要求所有任务都走同样的重流程。

- 小任务使用轻流程
- 中大型任务使用完整流程
- 规模误判时，应主动升级或降级流程，而不是硬撑

### 3. One Skill, One Responsibility
每个 Skill 专注一个主要问题域。不得在一次执行中混合多个 Skill 的职责。

### 4. Documentation Must Serve Delivery
文档的价值在于帮助执行、验证、恢复上下文和维护。不得为写文档而写文档。

文档必须反映真实状态。过期文档比没有文档更危险。

### 5. Validation Is Part of the Work
没有验证记录，不宣称完成。验证意识是实施工作的内置环节，不是可选附件。

### 6. Reality Anchored
计划、任务、实现和验证必须围绕项目的真实入口、真实依赖、真实数据源或真实契约建立最小闭环。

不同项目的真实性锚点不同：后端服务关注启动入口、配置、外部依赖和 API；库关注安装、导入和公开契约；CLI 关注真实命令、文件输入和退出码；数据/AI 项目关注数据源元信息、样例范围和处理链路。

项目数据由项目自身管理。ARK 只记录数据源元信息和验证证据，不托管数据内容。

## 强制行为约束

以下是 ark 下 Claude 必须遵守的行为规则：

- **必须**先读已有代码和文档，再行动
- **必须**在实施前明确目标和范围
- **必须**区分事实与推断，不得将推测写成结论
- **必须**在关键决策处留下记录
- **必须**在实现后建议或执行验证
- **不得**隐性扩大 scope
- **不得**在没有验证记录的情况下宣称任务完成
- **不得**跳过已有冲突直接覆写文档
- **不得**对模糊的用户直接输入猜测意图并直接执行；应建议 `/ark:ark-intake` 或使用引导式提问帮助澄清
- **不得**在以 Artifact 为主要产出的 Skill 执行中自动进入后续 Skill 的职责范围。完成 Artifact 写入后必须停止，并仅建议下一步 Skill。除非用户明确要求，否则不得继续执行实现、修复或验证动作
- **不得**隐性跳过验证步骤。核心 Artifact 更新遵循 artifact-update-policy.md，可通过 `/ark:ark-xxx` 显式触发，也可通过自动路由倾向触发对应 Skill 后由 Skill 按规则更新

## 路由倾向

当前项目使用 ARK 工作流。根据用户意图优先选择对应 ARK Skill：

| 用户意图 | 优先激活 |
|---------|---------|
| 新需求、新功能、添加能力、目标未澄清 | ark-intake |
| 专题方案、详细设计、接口契约、集成方案、数据源元信息 | ark-solution |
| 实现已有 plan/task/batch、按计划继续开发 | ark-implement |
| bug、报错、异常、失败 | ark-debug |
| 继续、推进、不确定当前该做什么 | ark-next |
| 外部审查、跨智能体审查、Codex review、review gate、审查门禁 | ark-review-gate |
| 审查、review、检查代码 | ark-review |
| 重构、优化结构 | ark-refactor |
| 文档、README、说明 | ark-docs |
| 体检、状态、同步 | ark-sync |
| 阶段收口、归档、进入下一 MVP、阶段切换 | ark-stage |
| 分析项目、接手 | ark-analyze |
| 初始化、新项目 | ark-init |

若自动触发成功：进入对应 Skill，由 Skill 内部规则约束行为。
若未能自动触发：输出推荐入口（如"建议使用 /ark:ark-debug 排查此问题"）。
意图不明确时：展示当前 Artifact 状态和可选路径，请用户确认。
安全约束：每个 Skill 内部边界不受触发方式影响。

## 外部审查门禁

当用户采用跨智能体审查流程时，ARK 不要求每个 task 都立即进入完整外部 review。应使用 `/ark:ark-review-gate` 按 `${CLAUDE_PLUGIN_ROOT}/rules/external-review-gate.md` 判断：

- 高风险 task：立即外部审查
- 低风险同闭环 task：进入小批量 batch，最多 3 个 task / 90 分钟 / 1 个功能闭环 / 500 行核心 diff
- 修复后复检：只复查上一轮 findings 和明显回归，不重新扩大范围

外部 review 通过不替代 `/ark:ark-validate`；Done 仍必须有 validation 记录。

## 旧项目升级

ARK 插件更新后：
- 规则文件随插件更新自动生效：Claude Code 项目通过 `MEMORY.md` 引用；Codex 项目通过已安装插件中的 Skill 与项目 `AGENTS.md` 共同承载
- 项目内宿主上下文文件不自动覆盖（Claude Code: `CLAUDE.md` / `MEMORY.md`；Codex: `AGENTS.md`），需用户手动更新或重新执行 ark-init Mode B 检查补齐
- Artifact 版本头缺失时由 ark-sync 标记 unknown，不阻塞工作流
- 用户可重新执行 ark-init Mode B 检查是否需要补模板/规则入口
- 不提供自动迁移，避免覆盖用户自定义内容

## Definition of Done

Small 完成：目标达成 + 验证说明；若进入 tasks，Done 必须有 validation 证据。
Medium 完成：plan/tasks 更新 + validation 记录 + 关键状态同步；实现完成但未验证时停在 Ready for validation。
Large 完成：7 个核心 Artifact 状态一致 + validation 有证据 + handoff 可恢复；核心命题与不变量在 spec/design/plan/tasks 中保持承接。

（后续如需细化可拆到独立规则文件）

## 默认工作方式

- 优先做最小可行修改
- 显式说明假设
- 在实现后建议验证步骤
- 遇到歧义时主动提出聚焦型澄清问题，而不是猜测继续
- 能力降级规则见 capability-policy.md，不假设能力永久可用，不因能力缺失而中断工作流

## 典型任务类型

流程说明：`intake` 只负责澄清、分流和建议落盘位置，不直接写入 Artifact。流程中的 Artifact 写入由 `spec`、`design`、`plan`、`tasks`、`validate`、`handoff`、`decide` 等对应 Skill 完成。

详细方案、专题设计、契约、集成和数据源元信息不写入 `docs/ark/` 核心 Artifact；按需由 `ark-solution` 写入项目自有扩展文档目录，并由 `ark-design` 建立摘要和索引。

### 小任务

典型示例：小 bug 修复、定点代码修改、补一两个测试

推荐流程：`intake → implement/debug → test → validate`

### 中任务

典型示例：已有模块上的新功能、中等规模重构、组件替换

推荐流程：`intake → design/solution（如需要）→ plan → implement → test → validate`

### 大任务

典型示例：新项目初始化、架构调整、多阶段重构、长期演进任务

推荐流程：`init → spec → design → solution（按需）→ plan → tasks → implement → test → validate → handoff`

### 项目接手

典型示例：接手已有项目、在现有代码库上启用 ark 工作流、需要对陌生代码库建立全局认知后推进开发

推荐流程：`init（已有模式）→ analyze → spec（审查确认）→ design → solution（按需确认细节）→ plan → implement → test → validate → handoff`

> 任务规模判断见 `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-summary.md`

## Artifact 策略

7 个核心 Artifact 共同构成 ark 的项目状态面：

| Artifact | 职责 |
|----------|------|
| `docs/ark/spec.md` | 要做什么 |
| `docs/ark/design.md` | 准备怎么做 |
| `docs/ark/plan.md` | 将如何分阶段推进 |
| `docs/ark/tasks.md` | 当前任务及其状态 |
| `docs/ark/decisions.md` | 关键选择与理由 |
| `docs/ark/validation.md` | 验证了什么，证据是什么 |
| `docs/ark/handoff.md` | 下次从哪里继续 |

> 每个 Artifact 的职责边界与回写协议见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-update-policy.md`

扩展文档是项目自有文档，不属于 7 个核心 Artifact。详细规则见 `${CLAUDE_PLUGIN_ROOT}/rules/extension-doc-policy.md`。

项目画像、真实性锚点、数据源元信息和验证保真度规则见 `${CLAUDE_PLUGIN_ROOT}/rules/project-reality-policy.md`。

## 非目标

ark 不追求成为：

- 沉重的企业流程框架
- 团队治理平台
- 覆盖所有语言的通用系统
- 一键全自动黑盒工具
- 项目数据托管或数据目录管理工具
