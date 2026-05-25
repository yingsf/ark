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

### Small 任务
1. 确认本轮唯一执行目标（单点修改）。
2. 读取并吸收相关 `validation.md` 未覆盖项、`handoff.md` 恢复提示、`decisions.md` 约束；若存在与当前目标冲突的前序结论，先停止并建议 `/ark:ark-sync`。
3. 执行 Reality Check：确认本次是否涉及真实入口、真实依赖、真实数据源或公开契约；若不涉及，说明原因。
4. 观察同模块或相邻模块的注释/docstring 风格；若项目风格不明确，使用 ARK 默认 `fastchain-enhanced` 中文 Google 风格。
5. 完成修改，保持最小改动范围，并同步补齐必要 docstring 和中文注释。
6. 在修改完成点执行局部质量整理（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行）；若工具修改了文件，重新读取当前内容或 diff。
7. 检查新增/修改的公共接口、关键方法和复杂逻辑是否符合注释/docstring 要求。
8. 执行 spec/design/extension 漂移检查：只识别本次实现是否改变需求、设计现实或扩展文档现实，发现后在输出中建议对应 Skill，不直接回写 spec/design 或扩展文档。
9. 若实现完成但尚未验证，tasks.md 只能更新为 Ready for validation，不得标记 Done。
10. 完成当前目标后停止，建议 `/ark:ark-test` 和 `/ark:ark-validate`；如需继续下一个任务，请用户再次执行 `/ark:ark-implement`。

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
12. **批次执行**：每完成一个批次后，在稳定点执行局部质量整理（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行），检查新增/修改的公共接口、关键方法和复杂逻辑是否符合注释/docstring 要求，执行 spec/design/extension 漂移检查，输出批次完成状态，更新 tasks.md 记录批次进展。然后建议下一批次或停止。
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

本节适用于 Medium / Large 任务中修改范围较大的场景。

### 触发信号

出现以下任一信号时，应优先考虑批次实施：

- 涉及 3 个以上文件
- 单文件大段重写（非增删个别函数）
- 存在明显顺序依赖（必须先完成 A 才能做 B）
- 预期单次修改难以在一个稳定回合内完成

### 硬约束

- 触发批次信号时，**不得**默认一次完成全部修改；应先拆成实施批次，并只完成当前批次
- 未指定 task、batch 或阶段范围时，**不得连续执行多个 Todo**；每轮默认只推进一个 task 或一个明确 batch
- batch 覆盖多个 task 时，必须在编码前声明覆盖任务、合并原因和批次边界；不得把后续任务隐式纳入当前批次

## 注释与 docstring 执行规则

写 Python 代码时，`/ark:ark-implement` 必须把注释/docstring 作为实现完整性的一部分，而不是事后装饰。

### 风格选择

- 优先读取当前项目 `CLAUDE.md` 和相邻代码的既有约定
- 若项目已有明确注释/docstring 风格，优先对齐项目风格
- 若项目没有明确约定、风格混乱或缺少样例，使用 ARK 默认 `fastchain-enhanced` 中文 Google 风格
- ARK 默认不主动新增顶部模块级 docstring；既有项目已存在的模块 docstring 可保持原状，除非本次任务明确要求清理
- 模块级背景说明如确有必要，优先放入设计文档、类/函数 docstring，或使用紧邻代码的上方块注释
- 第三方术语、协议名、类型名、异常名可保留英文；说明性文字默认中文

### 注释详细度分级

实现前先判断本次新增/实质修改对象的注释等级：

| 等级 | 适用对象 | 执行要求 |
|------|----------|----------|
| L0 无需补充 | 简单私有 helper、一眼可读的薄包装、简单 getter/setter、无业务语义的局部赋值 | 不强制 docstring，不写复述代码的注释 |
| L1 standard | 公共函数、公共方法、pydantic model、dataclass、protocol、API handler、service/repository 方法 | 使用中文 Google 风格 docstring，按需写 `Args:` / `Returns:` / `Raises:` |
| L2 fastchain-enhanced | 核心 service/manager/provider/adapter、配置/日志/Apollo/MySQL/Redis/MinIO/ES 等资源封装、连接池/事务/重试/降级/幂等/缓存 | 类级 docstring 说明职责、存在原因、封装边界、生命周期或协作关系；关键属性写 `Attributes:` |
| L3 架构级说明 | 应用启动链路、资源初始化链路、数据导入链路、任务调度链路、跨模块核心编排逻辑 | 说明运行阶段、不变量、失败语义和分层原因；过长细节应放入 design/solution 文档 |

### 必须补充 docstring 的对象

- 新增或实质修改的公共类
- 新增或实质修改的公共函数
- 新增或实质修改的关键方法（即使方法以下划线开头，只要承载核心流程、资源生命周期、并发/降级/失败处理，也应说明）
- 对外暴露的 dataclass、pydantic model、协议类、运行时封装、服务类、仓储类、客户端类

### 模块级与变量说明边界

- 新建 `.py` 文件不得以三引号模块 docstring 开头；文件职责由路径、命名、必要块注释和设计文档共同表达
- 不使用赋值语句后的三引号字符串说明常量、变量、集合、配置项或枚举值；这类变量后置三引号容易被误认为孤立字符串，且不符合 ARK 默认风格
- 常量、变量或集合说明确有维护价值时，写在定义上方的中文块注释；简单枚举值和显而易见常量不补说明
- 对既有项目中已有模块 docstring 或变量后置三引号，除非本次修改直接涉及并且项目约定允许，不为风格统一扩大清理范围

### 中文 Google / fastchain-enhanced 风格要求

- 类级 docstring 第一行说明核心职责，随后说明设计目的、封装边界、生命周期或协作关系
- L2/L3 对象不得只写一句空泛摘要，必须解释“为什么存在”“封装什么边界”“哪些约束不能破坏”
- 复杂类可按需使用“增强特性”“核心设计特点”“设计考量”等中文段落，帮助维护者快速理解设计重点
- 涉及关键状态、资源或公开属性时，类级 docstring 应包含 `Attributes:`
- `Methods:` 可用于 L2/L3 复杂类，但不强制为所有类列出方法清单
- 函数和方法按需使用 `Args:`、`Returns:`、`Raises:`；内容说明参数语义、返回含义、失败条件和边界，不只翻译变量名
- 复杂函数必须说明核心算法、关键假设、边界条件、性能/并发/外部系统约束
- 简单私有 helper 可以保持简短，不强制写完整段落

### 中文标点与尾随注释规则

- 中文 docstring 和中文注释的描述句默认不使用句末中文终止标点
- 禁止在 docstring 摘要、详细描述、`Args:`、`Returns:`、`Raises:`、`Note:`、`Warning:` 的描述行末使用 `。`、`！`、`？`、`；`
- 中文块注释也不使用句末中文终止标点
- 允许在句中使用中文逗号、顿号、冒号和括号
- 业务解释类注释优先写在相关代码上方，不写解释性尾随注释
- 工具指令类注释不受尾随注释限制，例如 `# noqa`、`# type: ignore[...]`、`# pylint: disable=...`、`# fmt: off/on`

### 必须补充中文注释的场景

- 复杂分支、边界条件、异常转换、降级策略
- 连接池、事务、文件句柄、锁、限流器、后台任务等资源生命周期
- 并发、缓存、一致性、幂等、重试、超时等容易误改的约束
- 为兼容历史行为、绕开第三方限制或降低风险而做的非直观实现

### 禁止事项

- 不用英文短句替代项目默认中文说明
- 不写复述代码表面行为的低信息注释
- 不为了补注释而扩大 scope 或批量重写无关文件
- 不把所有局部变量、简单 getter/setter、显而易见赋值都文档化
- 不用装饰性长文掩盖接口职责不清的问题；职责不清时优先整理接口边界
- 不主动新增顶部模块级 docstring
- 不在赋值语句后写三引号字符串说明常量、变量、集合或配置项
- 不在中文 docstring / 中文注释的描述句行末添加中文终止标点
- 不写业务解释型尾随注释；需要解释原因、约束或风险时写在代码上方

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
- 当前批次可以覆盖多个 task 仅限：用户明确指定多个 task、tasks.md 已记录当前批次、plan 明确声明该阶段作为一个 batch、或多个 task 不可独立验证必须合并执行
- 覆盖多个 task 的批次必须声明：当前批次、覆盖任务、合并原因、批次边界；批次边界外的任务不得实现
- 每个批次结束后执行局部质量整理和检查（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行）
- 每个批次结束后检查新增/修改的公共接口、关键方法和复杂逻辑是否满足注释/docstring 要求
- 每个批次结束后更新 Reality Check 结果：真实锚点已推进 / 仍为替身 / 无直接锚点，并记录退出条件
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

每个 batch 完成后，根据任务大小决定 checkpoint 条件：

- **Small 任务**：batch 完成 → 可选 checkpoint commit
- **Medium/Large 任务**：batch 完成 → 相关 test 子集通过 → validate evidence 草稿可用 → 建议 checkpoint commit

commit 范围：该 batch 修改的文件
commit 格式：`<type>(<scope>): <batch-goal>`
不自动提交，等用户确认

每个完成点的输出必须给出：
- 建议 checkpoint commit：是 / 否
- 建议 message：
- 建议纳入文件：
- 不建议纳入文件：

## 验证要求
- 实现内容应与已定义目标一致
- 任何额外扩 scope 都应显式指出
- 改动后的行为应具备验证路径
- 实现完成但未执行 `/ark:ark-validate` 或没有对应验证记录时，不得将 tasks.md 任务标记为 Done；最多进入 Ready for validation
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

### 1. 本次实现目标
- 本轮唯一执行目标：
- 选择理由：
- 本轮不处理：
### 2. 主要修改（文件 + 变更摘要）
### 2.1 前序结论吸收
- `validation.md` 未覆盖项：
- `handoff.md` 恢复提示：
- `decisions.md` 约束：
- 本次已处理：
- 本次未处理及原因：
### 2.5 批次进展（批次实施时）
- 当前批次：Batch n/m
- 本批目标：
- 覆盖任务：
- 合并原因：
- 批次边界：
- 已修改文件与锚点：
- 本批完成信号 / 未完成项：
### 2.6 Reality Check
- 项目类型：
- 本次真实性锚点：
- 真实依赖 / 数据源 / 契约状态：
- 替身边界与退出条件：
### 2.7 注释与 docstring
- 注释详细度判定：L0 / L1 / L2 / L3
- 已补充对象：
- 未补充对象及原因：
- 模块级 docstring / 变量后置三引号检查：
- 标点与尾随注释检查：
### 3. 假设 / 限制 / 延期项
### 4. Artifact 回写
- `plan.md`：已更新 / 无需更新
- `tasks.md`：已更新 / 无需更新
- `tasks.md` task ID 唯一性：已确认 / 未检查（原因）
- `decisions.md`：建议更新 / 无需更新
- `spec.md`：若发现漂移，建议 `/ark:ark-spec` 并说明原因；无漂移可省略
- `design.md`：若发现漂移，建议 `/ark:ark-design` 并说明原因；无漂移可省略
- 扩展文档：若发现漂移，建议 `/ark:ark-solution` 并说明原因；无漂移可省略
### 5. 建议下一步

- 若本次修改涉及可测试逻辑（新增/修改的公共方法、条件分支、错误处理）→ `/ark:ark-test` → `/ark:ark-validate`
- 若本次修改不涉及可测试逻辑（纯配置、文档、样式）→ `/ark:ark-validate`
- 若会话即将中断 → `/ark:ark-handoff`

### 5.5 Checkpoint 建议
- 建议 checkpoint commit：是 / 否
- 建议 message：
- 建议纳入文件：
- 不建议纳入文件：

### 6. Sub-agent 状态
- Sub-agent 状态：已启用（N 个 worker）/ 未启用（原因：...）

## 备注
`/ark:ark-implement` 的目标不是「尽可能多写代码」，而是「以最低风险推进真实进展」。

PostToolUse ruff hook 只做格式化，不做 lint auto-fix。lint auto-fix 由 implement 在批次完成等稳定点执行，避免编辑中间态被删除未使用导入等自动修复干扰。

若非 Python 文件编辑与项目 formatter / hook 存在冲突，应优先将其视为工具链问题；在当前约束下若必须采用替代写入方式，应明确说明原因，且不得把绕过 hook 当成默认实现路径。
