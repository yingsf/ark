---
name: ark-helper
description: |
  根据用户当前场景和项目状态，推荐最合适的 ARK 流程路径。
  触发时机：不确定下一步用什么 Skill、遇到流程异常、想查看某类场景的推荐流程。
  关键词：帮助、helper、怎么用、用什么指令、流程、场景、指引、导航、不知道怎么做。
version: "1.0"
---

# /ark-helper

## 目标
根据用户当前所处场景和项目状态，推荐最合适的 ARK 流程路径，并解释每一步的原因与边界。

**硬约束：本 Skill 只负责场景判断与流程推荐，不自动执行任何后续 Skill，不更新任何 Artifact。**

helper 优先推荐标准安全路径，而不是最短乐观路径；在高风险场景下，应显式提示关键不可省略步骤与主要分叉。

## 适用场景
- 不确定下一步该用哪个 Skill
- 遇到流程异常（忘记先 intake、超时中断、不确定项未处理等）
- 想快速查看某类场景的推荐流程
- 拿不准两个 Skill 之间的选择（如 spec 还是 design）

## 不适用场景
- 目标明确，知道该用什么 Skill
- 需要执行具体工作（那是其他 Skill 的职责）

## 前置建议
- 无前置要求，随时可执行

## 输入
- 用户的问题或场景描述（可选）
- `docs/ark/tasks.md`（按需读取）
- `docs/ark/handoff.md`（按需读取）
- `docs/ark/plan.md`（必要时补读）
- 任务级 Artifact 是否存在或仅为空模板（用于识别"刚启用 ARK，尚未进入任务周期"）

## 输出
- 当前场景判断
- 推荐流程路径（2-5 步命令链）
- 每一步的简要原因说明

## 相关 Artifact
- 可按需读取：`docs/ark/tasks.md`、`docs/ark/handoff.md`、`docs/ark/plan.md`（仅当问题明显依赖当前项目状态时）
- **不更新任何 Artifact**

## 工作流

1. **判断是否需要读取项目状态**：优先根据用户提供的场景描述判断。仅当问题明显依赖当前项目状态（如中断恢复、当前该做什么、是否处于 Doing/Blocked）时，才读取 `docs/ark/tasks.md` 和 `docs/ark/handoff.md`，必要时补读 `docs/ark/plan.md`。
2. **优先匹配入口场景**：若用户未提供描述，且项目状态显示"已植入 ARK 但尚未建立实质性任务级状态"（docs/ark/tasks.md、docs/ark/handoff.md、docs/ark/plan.md 不存在或仅为空模板），优先匹配"刚启用 ARK，尚未进入任务周期"场景，不再走通用场景猜测流程。
3. **识别其他场景**：
   - 若用户提供了场景描述 → 结合描述匹配场景卡片
   - 若用户未提供描述 → 基于已读取的项目状态推断场景
   - 若无法明确匹配 → 按固定模板列出 2-3 个可能的场景，并附带最小安全入口建议
4. **生成推荐**：按固定输出格式给出场景判断、推荐流程和原因说明。

### 无法明确匹配时的输出模板

```
当前判断：你现在更像以下场景之一：

1. {场景名} — {一句话描述}
2. {场景名} — {一句话描述}

若你现在还不确定，建议先走一个最小安全入口：
- 若尚未正式初始化当前项目：`/ark:ark-init`
- 若想先理解代码库：`/ark:ark-analyze`
- 若已有明确任务：`/ark:ark-intake`

你也可以补充以下信息帮助判断：
- 当前是否已有明确任务计划
- 当前是否已在实现中
- 当前是否是中断恢复
```

## 场景卡片

> 内部编号用于场景匹配，输出时不强制显示编号。

### A. 项目启动类

**A0. 刚启用 ARK，尚未进入任务周期**

项目已植入 ARK 工作流，但尚未建立实质性的任务级状态（如 tasks.md、handoff.md、plan.md 不存在或仅为空模板），用户也未提供明确场景描述。

推荐路径：
1. 先确认初始化状态：
   若尚未完成正式初始化（如 docs/ 目录不存在或 CLAUDE.md 未生成）→ 先 `/ark:ark-init`
2. 初始化完成后（或已确认完成），根据目标分流：
   - 若想先理解代码库 → `/ark:ark-analyze`
   - 若已有明确需求或任务 → `/ark:ark-intake`

为什么：
- `/ark:ark-init` 用于完成或确认项目正式进入 ARK 工作流，是后续所有任务级操作的前置条件
- `/ark:ark-analyze` 适合在初始化完成后建立全局认知
- `/ark:ark-intake` 适合在初始化完成后带着明确任务进入正式澄清

**A1. 接手已有项目**

用户对代码库不熟悉，需要建立全局认知后再推进开发。

推荐路径：
1. `/ark:ark-init`（模式 B，植入工作流）
2. `/ark:ark-analyze`（增量锚定分析，预填充 spec/design）
3. 若边界未清 → `/ark:ark-spec`（审查确认）
4. 若机制未清 → `/ark:ark-design`（审查确认）
5. 需求和范围已明确后 → `/ark:ark-plan`

**A2. 已有项目上新功能**

项目已在使用 ARK 工作流，需要启动一个新的需求开发。

推荐路径：
1. 默认先 `/ark:ark-intake`（澄清需求的目标、范围和约束）
2. 根据规模与清晰度决定：
   - Small（目标、范围、成功标准已明确）：`/ark:ark-implement` → `/ark:ark-test` → `/ark:ark-validate`
   - Medium：`/ark:ark-plan` → `/ark:ark-implement` → `/ark:ark-test` → `/ark:ark-validate`
   - Large（边界与机制都需要正式化）：`/ark:ark-spec` → `/ark:ark-design` → `/ark:ark-plan` → `/ark:ark-tasks` → `/ark:ark-implement` → ...

### B. 需求与设计类

**B1. 新需求但边界未清**

需求方向有，但具体做什么、做到什么程度不清楚。

推荐路径：
1. `/ark:ark-intake`（澄清目标、范围、约束）
2. 根据结果 → `/ark:ark-spec` 或 `/ark:ark-plan`

为什么先 intake：intake 帮你搞清楚"要做什么"，再决定是先写规格还是直接规划。

**B2. 不确定用 spec 还是 design**

用户不清楚当前需要 `/ark:ark-spec` 还是 `/ark:ark-design`。

判断依据：
- 如果纠结的是"做什么、做到什么程度"→ `/ark:ark-spec`
- 如果纠结的是"怎么做、模块怎么分"→ `/ark:ark-design`
- 如果两者都模糊 → 先 `/ark:ark-spec` 再 `/ark:ark-design`（先定边界再定方案）

### C. 分析与确认类

**C1. analyze 后有不确定项**

`/ark:ark-analyze` 输出了不确定项（U 编号），用户不知道怎么处理。

推荐路径：
1. 按 A-E 分组查看不确定项
2. 批量回答 U 编号（可一次性回答多个；建议优先处理 D 类真实问题或阻塞当前理解的 A/B 类）
3. Claude 只会生成建议更新方案（明确每条去向），不会自动执行 `/ark:ark-spec`、`/ark:ark-design` 或其他后续 Skill；确认后再显式执行对应 Skill（`/ark:ark-spec`、`/ark:ark-design`）完成正式更新
4. 根据不确定项类型：
   - A 类（规格边界）→ `/ark:ark-spec`
   - B 类（设计机制）→ `/ark:ark-design`
   - C 类（两者都涉及）→ 先 `/ark:ark-spec` 再 `/ark:ark-design`

**C2. spec 或 design 被预填充后怎么确认**

analyze 已预填充 spec.md 或 design.md，用户不确定后续怎么走。

推荐路径：
1. 若 spec.md 或 design.md 已有实质性内容，可执行 `/ark:ark-spec` 或 `/ark:ark-design` 进入审查确认流程
2. 更稳妥的做法是明确说明要确认的边界或机制（如 `/ark:ark-spec 确认 API 认证范围`），让其先给出更新方案再执行
3. 确认后，再根据目标是否已明确、是否需要分阶段推进，进入 `/ark:ark-plan`、`/ark:ark-tasks` 或其他后续流程

### D. 实现与质量类

**D1. 开发中发现 bug**

实现中途发现一个 bug，不确定该停下来处理还是先完成当前工作。

判断依据：
- bug 与当前任务相关且阻塞继续 → 先 `/ark:ark-debug` 定位修复
- bug 与当前任务相关，但当前批次已接近完成且不影响安全收口 → 可先完成当前批次并记录，再进入 `/ark:ark-debug`
- bug 独立于当前任务 → 记录下来，当前任务完成后再处理
- bug 影响范围不明 → 先 `/ark:ark-debug` 评估影响范围

若决定暂不处理，应将该 bug 记录为 `docs/ark/tasks.md` 中的新 Todo 任务；若当前会话即将中断，再通过 `/ark:ark-handoff` 记录其对当前任务的影响。

**D2. 实现中发现 scope 膨胀**

实现过程中发现任务比预期大，不确定该继续还是停下来重新规划。

推荐路径：
1. 停下来评估膨胀程度
2. 若膨胀超出当前任务范围 → 停止实现，回到 `/ark:ark-plan` 或 `/ark:ark-intake` 重新规划
   - 若只是实施拆分不合理 → `/ark:ark-plan`
   - 若连目标、边界都变了 → `/ark:ark-intake`
3. 若可通过批次实施消化 → 按 implement 批次机制拆分继续
4. 若涉及架构变化 → 建议先 `/ark:ark-design`

为什么停下来：隐性扩大 scope 是 ARK 明确禁止的行为。

**D3. 合并前准备**

功能已实现，准备合并到主分支。

推荐路径：
1. `/ark:ark-test`（如适用，确保测试通过）
2. `/ark:ark-review`（代码评审）
3. `/ark:ark-validate`（验证记录）
4. 根据结果分支：
   - 有 Critical/Major 问题 → 先修复（回到 `/ark:ark-implement` 或 `/ark:ark-debug`），再重新执行 review → validate
   - 仅有 Minor/Suggestion → 可合并后处理
5. 合并/提交是后续动作，不是 helper 直接推荐的第一步

分叉路径：
- review 发现 bug → `/ark:ark-debug` 定位修复，修复后回到 review
- review 发现设计偏差 → 视严重程度回到 `/ark:ark-design` 或 `/ark:ark-plan`
- 验证未通过 → 回到对应修复环节，不跳过

### E. 中断与恢复类

**E1. 网络中断 / implement 超时恢复**

会话中断或 implement 超时，不确定怎么恢复。

推荐路径：
1. 查看 `docs/ark/handoff.md`（了解上次停在哪里）
2. 查看 `docs/ark/tasks.md`（确认当前任务状态）
3. 若状态可能有漂移 → `/ark:ark-sync`
4. 若状态可信 → `/ark:ark-next`
5. 恢复 implement 时，只恢复当前批次，不要一次重做全部

匹配约束：若不存在 handoff.md、tasks.md 的中断/进行中信号，且用户未提到"继续、恢复、上次、中断"等语义，不应优先匹配此场景。

**E2. 忘记先用 /ark:ark-intake**

用户直接描述了需求或问题，没有使用 /ark 命令，想了解接下来怎么做。

推荐路径：
1. 执行 `/ark:ark-intake` 补一次正式澄清
2. intake 会整理目标、范围、约束和推荐路径
3. 根据结果进入对应的后续流程

为什么补 intake：先通过正式澄清把前面对话中的信息整理成明确的目标、范围和约束，再决定是否进入正式流程。这比凭理解直接执行风险更低。

## 验证要求
- 推荐的流程路径必须是 ARK 已定义的合法 Skill 组合
- 场景判断必须基于用户描述或项目状态，不得凭空猜测
- 每条推荐必须说明原因，不得只给命令链不加解释
- 不得自动执行任何后续 Skill
- 不得更新任何 Artifact
- 仅当问题明显依赖当前项目状态时才读取 Artifact，通用问题不得强制读取
- 在实现完成、合并前准备、中断恢复、analyze 后确认等高风险场景下，应优先推荐标准安全路径，不得因当前状态看似良好而跳过 review、validate、debug 分叉等关键步骤
- 当匹配到场景卡片时，推荐流程必须遵循该卡片的预设路径，不得用自定义流程替代。若基于当前项目状态判断某个步骤可跳过，必须先输出卡片的完整路径，再标注建议跳过的步骤及理由
- 若项目状态符合"刚启用 ARK，尚未进入任务周期"特征（已植入 ARK 但任务级 Artifact 不存在或仅为空模板），应优先匹配 A0 场景，不得误判为 A1 接手已有项目、E1 中断恢复或 A2 已有项目上新功能
- A0 场景下，不得将 `/ark:ark-analyze` 或 `/ark:ark-intake` 与 `/ark:ark-init` 并列为同级默认入口；应先确认初始化状态，再给后续分流建议

## 停止条件
- 已输出场景判断、推荐流程和原因说明
- 用户的问题已被回答

## 固定输出格式

### 1. 当前判断
你现在处于什么场景（1-2 句话）。

### 2. 推荐流程
2-5 步的命令链，例如：
1. `/ark:ark-intake` → 2. `/ark:ark-plan` → 3. `/ark:ark-implement`

### 3. 为什么
每一步的简要原因说明（每步 1 句话）。

### 4. 边界声明
本次仅提供流程建议，不会自动执行后续 Skill。

### 5. 关键分叉（高风险场景时）
若 {关键检查} 出现问题 → {回流路径}（最多 2-3 条）

## 备注
/ark:ark-helper 是导航 Skill，不是执行 Skill。它的价值在于帮你快速找到正确的路，而不是替你走路。如果推荐结果仍不确定，可以带着具体问题再问一次。
