# Artifact 职责速查

每个 Artifact 主要回答一个问题。写入时先判断「这条内容回答的是哪个问题」，再选择对应文件。

| Artifact | 回答的问题 | 主更新者 | 不应用于 |
|----------|-----------|----------|----------|
| `docs/ark/spec.md` | 要做什么 | `/ark:ark-spec`（可由 `/ark:ark-analyze` 预填充）| 记录实施步骤、任务状态、测试结果 |
| `docs/ark/design.md` | 准备怎么做 | `/ark:ark-design`（可由 `/ark:ark-analyze` 预填充）| 记录执行进度、细碎任务清单、最终验证结果 |
| `docs/ark/plan.md` | 将如何分阶段推进 | `/ark:ark-plan`（也可由 implement、debug、sync 回写）| 代替 tasks 管理细粒度状态、代替 handoff 做恢复摘要 |
| `docs/ark/tasks.md` | 当前有哪些任务，分别处于什么状态 | `/ark:ark-tasks`（也可由 implement、debug、sync 小幅更新）| 代替 spec 定义需求、代替 plan 定义阶段策略 |
| `docs/ark/decisions.md` | 关键选择是什么，为什么这么选 | `/ark:ark-decide` | 记录执行进度、记录验证结果 |
| `docs/ark/validation.md` | 验证了什么，证据是什么 | `/ark:ark-validate` | 记录「准备验证什么」（那是 plan 的职责）|
| `docs/ark/handoff.md` | 下次从哪里继续 | `/ark:ark-handoff` | 代替 plan 作为主执行文档、代替 tasks 管理状态 |

`docs/ark/stages.md` 是可选阶段索引，仅由 `/ark:ark-stage` 按需创建和维护；它不属于初始化默认 7 个核心 Artifact。阶段历史详情保存在 `docs/ark/archive/<stage-id>/`，当前执行依据仍是当前 7 个核心 Artifact。

扩展文档（如 `docs/solution/*`、`docs/design/*`、`docs/contracts/*`、`docs/data-sources/*`）不属于核心 Artifact。它们由 `/ark:ark-solution` 按需创建和维护，`docs/ark/design.md` 只保留摘要和索引，不复制正文。

## 核心约束

- **不得混用**：每个 Artifact 主要回答一个问题，不应将多个职责写入同一文件
- **冲突必须先显式化**：发现文档与代码现实不符时，必须先指出冲突，再修正，不得直接跳过
- **没有验证记录，不宣称完成**：中大型任务如无 `docs/ark/validation.md` 记录，不得写出「已完成且无风险」的结论
- **Done 必须有证据**：`tasks.md` 中 `Done` 任务必须指向 `validation.md` 中的真实验证记录；实现完成但尚未验证的任务应进入 `Ready for validation`
- **核心命题不可丢失**：spec 中确认的核心命题与不变量必须被 design、plan、关键 tasks 承接；若后续 Artifact 弱化或遗漏，应标记 stale 并建议同步
- **过期文档必须说明**：如果 Artifact 长期未维护，必须明确标注其陈旧状态，不得假装有效

## 一句话规则

`spec` 管目标 · `design` 管方案 · `plan` 管推进 · `tasks` 管状态 · `decisions` 管取舍 · `validation` 管证据 · `handoff` 管恢复

`solution/contracts/data-sources` 等扩展文档管专题细节，不进入 7 个核心 Artifact。

## Artifact 元信息

核心 Artifact 顶部应包含：

```md
<!-- ark-artifact: <name> -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->
```

`last-updated` 用于 `ark-sync` 和 `ark-next` 判断上游变更是否已经传播到下游。旧项目或旧模板缺少该字段时，可信度可标为 `unknown` 或 `stale`，但不得仅因版本头差异覆盖用户内容。

### 日期语义

- `schema-version` 表示 Artifact 结构版本，只有模板结构或解析协议变化时才升级
- `last-updated` 表示该 Artifact 内容最后一次真实修改的日期
- `last-updated` 不是 revision、序号或同日排序字段
- 同一天多次修改同一 Artifact 时，`last-updated` 保持当天日期不变
- 禁止根据旧日期递增，禁止写入未来日期
- 若需要判断同一天内的先后顺序，应依据 git history、文件 diff、内容一致性或显式变更记录，而不是 `YYYY-MM-DD`

## 核心命题与不变量

`核心命题与不变量` 是跨项目类型的总称：
- 产品 / 平台：产品精髓、核心价值、不可拆分能力
- 后端服务：业务闭环、外部契约、真实依赖边界
- CLI：命令行为、输入输出、退出码语义
- SDK / library：公开 API、兼容性承诺
- 数据 / AI 项目：数据源、样例代表性、评估闭环
- Claude 插件：命令入口、宿主约束、Artifact 语义

承接规则：
- `spec.md` 定义核心命题与不变量
- `design.md` 说明技术方案如何保护这些不变量
- `plan.md` 说明实施阶段只代表推进顺序，不裁剪已确认范围
- `tasks.md` 的关键任务应能回溯到核心命题或真实性锚点
- `sync` 发现承接断裂时标记 stale/conflicting 并推荐对应 Skill

## Design vs Decide 边界

- **design.md**：记录方案如何工作，以及局部技术权衡
- **扩展文档**：记录某个专题的详细方案、模块级设计、接口契约或数据源元信息；由 design.md 建索引
- **decisions.md**：项目级长期记忆和当前仍有效决策索引，只记录满足以下全部条件的选择——不可逆或高回退成本、影响长期维护方向、未来可能被团队质疑或推翻

一般性技术权衡留在 design.md，不重复进 decisions.md。触发 ark-decide 时需判断：如果该选择在 3 个月内不太可能被重新审视，留 design.md 即可。

阶段切换时，`decisions.md` 不随阶段结束清空。`ark-stage` 应保留仍有效的项目级长期决策，不确定时默认保留；已被替代的长期决策标记为 `superseded` / 已替代，阶段性决策只在明确不再约束当前阶段时留在 archive。

## Artifact 可信度

四态定义：

| 状态 | 定义 |
|------|------|
| fresh | 内容与文件现实 / Artifact 一致性 / 验证记录一致 |
| stale | 最近代码变更影响该 Artifact，但 Artifact 未反映 |
| conflicting | Artifact 之间描述矛盾 |
| unknown | 缺少足够证据判断 |

判断依据（按优先级）：

1. 当前文件现实
2. Artifact 之间一致性
3. 已执行验证记录
4. git diff / git log（如可用）

无 git 的项目依据 1-3 即可判断，不必然 unknown。

关键 Skill 入口要求：
- ark-implement：开始前检查 plan.md + tasks.md + validation.md + handoff.md 可信度；实现后检查本次改动是否引发 spec.md / design.md / extension 漂移；实现完成但未验证时最多推进到 Ready for validation
- ark-validate：检查 tasks.md 可信度；验证通过后可建议或执行 Ready for validation → Done 的状态迁移，并写入 validation 记录
- ark-next：检查 handoff.md + tasks.md + plan.md + validation.md 可信度；若 spec.md / design.md 或扩展文档明显 stale/conflicting，应优先推荐 ark-sync
- ark-sync：输出完整 Artifact 可信度矩阵、扩展文档可信度摘要和上游变更传播判断；对 spec/design/validation 只建议对应 Skill，不直接捏造正文或验证事实
- ark-solution：维护扩展文档正文；不直接回写 `docs/ark/*`
- ark-stage：阶段级收口、归档、继承和新阶段初始化；写入前必须 preview 并等待确认，不得把 blocked/conflicting 阶段静默写成 closed
- 非 fresh 时推荐 ark-sync

> 完整的回写条件与禁止性约束见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-update-policy.md`

> 扩展文档规则见 `${CLAUDE_PLUGIN_ROOT}/rules/extension-doc-policy.md`，真实性锚点规则见 `${CLAUDE_PLUGIN_ROOT}/rules/project-reality-policy.md`。
