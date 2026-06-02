# Artifact Placeholder Policy

本文件定义 ARK 如何识别初始模板、占位内容和实质性内容，供 `ark-analyze`、`ark-spec`、`ark-design`、`ark-sync`、`ark-next` 和自检脚本共同使用。

## 目标

避免把 Artifact 模板中的示例文本、状态选项、日期占位和注释说明误判为项目真实状态。

## 非实质性内容

以下内容单独出现时，不构成实质性内容：

- 版本头：`ark-artifact`、`schema-version`、`last-updated`
- 日期占位：`YYYY-MM-DD`
- 通用占位：`待填写`、`待确认`、`...`、`<标题>`、`<project_name>`
- 编号占位：`标准 1`、`标准 2`、`问题 1`、`问题 2`、`项目 1`、`方案 A`
- 状态选项：`not started / in progress / blocked / done`、`fresh / stale / conflicting / unknown`
- 示例路径：`docs/solution/example.md`、`tests/test_xxx.py`
- 注释说明：`<!-- ... -->`
- 空状态：`无`、`当前无`、`暂无决策记录`

## 实质性内容判定

Artifact 满足任一条件时，才可视为有实质性内容：

1. 包含明确的项目能力、范围、非目标、验收标准、设计机制、真实入口、任务 ID 或验证命令
2. 包含 `/ark:ark-analyze` 标注的预填充来源，并且正文不是模板占位
3. 包含真实文件路径、真实模块名、真实命令、真实验证结果或用户确认过的结论
4. 至少两个非模板章节被真实内容填充，且这些内容不是上方“非实质性内容”列表中的 token

## Skill 使用要求

- `ark-analyze` 只有在目标 Artifact 为空或仍为初始模板内容时，才可预填充 `spec.md` / `design.md`
- `ark-spec` 和 `ark-design` 无输入时，必须先按本规则判断现有内容是否实质性存在
- `ark-sync` 判断可信度时，必须区分模板占位、旧内容和真实状态
- `ark-next` 推荐下一步时，不得把模板中的状态选项、示例路径或空状态当作项目事实
- `ark-check.py` 应检查高风险模板占位是否仍以正文形式出现在 Artifact 模板中

## 输出要求

当 Skill 因模板占位而判断 Artifact 无实质内容时，应说明依据，例如：

```text
判断：docs/ark/spec.md 仍为初始模板
依据：仅包含版本头、注释说明和待填写占位，未发现真实能力边界或验收标准
```
