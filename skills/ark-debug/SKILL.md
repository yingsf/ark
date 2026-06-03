---
name: ark-debug
description: |
  定位 bug，识别可能根因，推动形成低风险修复方案。
  触发时机：系统行为不正确、某个失败需要根因分析、已有缺陷现象或复现路径时。
  关键词：bug、调试、debug、报错、异常、根因、定位问题、出错了。
version: "1.0"
---

# /ark-debug

## 目标
定位 bug，识别可能根因，并推动形成低风险修复方案。

## 前置建议
- 如果问题现象或复现路径不清晰，建议先执行 `/ark:ark-intake` 澄清问题描述

## 适用场景
- 系统行为不正确
- 某个失败需要根因分析
- 已有缺陷现象或复现路径
- `/ark:ark-validate` 发现验证失败，需要定位和修复问题
- `/ark:ark-review-gate import` 已导入外部审查 findings，需要按“必须修复”项做最小修复

## 不适用场景
- 没有任何具体症状
- 当前任务主要是架构规划而非缺陷定位

## 输入
- bug 描述、观察到的症状、复现步骤（如有）、相关代码与日志、最近变更（如已知）
- 外部 review findings 分类（如来自 `/ark:ark-review-gate import`）：只处理“必须修复”，不顺手处理“可延期”或“不处理”项

## 信息收集策略

三档输入要求：

**最低可诊断输入（可推进分析）**：
  - 现象（至少 1 句）
  - 错误信息或复现步骤（二选一）

**缺少复现步骤**：
  - 进入假设分析
  - 所有假设标注 [low-confidence]
  - 输出"下一步最小采证动作"（如"请在 X 环境执行 Y 命令，观察是否出现 Z"）

**缺少现象描述**：
  - 停止并要求补充
  - 引导使用 debug report 模板（templates/snippets/debug-report.snippet.md）

建议提供（缺一则提示但不阻塞）：期望行为、相关版本、最近变更、已尝试排查、可疑模块。

## 输出
- 症状摘要、可能根因、影响范围、修复方向、验证方式
- 可选：代码修改
- 必要时：Artifact 回写建议

## 相关 Artifact
- 可读取：`docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`、`docs/ark/tasks.md`
- 可在必要时回写：`docs/ark/plan.md`、`docs/ark/tasks.md`
- 若修复路径引入重要取舍：建议更新 `docs/ark/decisions.md`
- 若修复暴露需求或设计漂移：建议 `/ark:ark-spec` 或 `/ark:ark-design`，不得直接回写 `spec.md` / `design.md`
- 若修复证明专题方案、接口契约、集成或数据源元信息过期：建议 `/ark:ark-solution`
- 应为 `docs/ark/validation.md` 提供输入

## 工作流
1. 清楚定义观察到的症状（不要跳过这一步直接猜根因）。
2. 收集或确认复现条件。
3. 识别相关执行路径或模块边界。
4. 基于证据提出根因假设，明确标注哪些是假设、哪些已确认。
5. 限定影响范围与变更边界：最小修复优先，不得顺带清理无关代码。
6. 如果输入来自外部 review findings，先按“必须修复 / 可延期 / 不处理”复核边界；只修复必须修复项，除非用户明确要求，不处理延期项。
7. 形成修复方案，必须包含对应验证方式（如何确认已修复）。
8. 修复完成后建议执行 `/ark:ark-test` 补充回归测试。
9. 若修复来自 external review gate，建议 `/ark:ark-review-gate recheck` 生成定向复检包，不建议直接重新全量 review。
10. 检查是否需要回写 Artifact（见下方回写规则）。
11. 执行修复后 spec/design/extension 漂移检查：只识别 bug 修复是否改变需求、设计现实或扩展文档现实，发现后建议对应 Skill，不直接回写 spec/design 或扩展文档。

## 外部 findings 修复模式

当输入来自 `/ark:ark-review-gate import` 或用户明确要求修复外部审查 findings 时，进入外部 findings 修复模式。

执行要求：
- 保留外部 finding 的编号、来源、严重级别、文件行号和原始问题摘要；没有编号时先为本轮修复生成稳定编号（如 `F1`、`F2`）。
- 只处理“必须修复”项；“可延期”和“不处理”项不得顺手修复，除非用户明确改变范围。
- 每个必须修复 finding 必须绑定修复目标、修复位置、验证方式和复检关注点。
- 若某个必须修复 finding 无法修复，必须标为 `still-open` 或 `blocked`，说明阻塞原因，不得把它写成已关闭。
- 修复完成后不得直接声称外部审查通过；正确路径是 `/ark:ark-test` 补充或运行回归 → `/ark:ark-review-gate recheck` 生成定向复检包 → `/ark:ark-validate` 记录最终 evidence。
- 若本轮只修复部分 findings，必须输出未闭合项，禁止进入 validate 完结建议。

Finding 闭合状态必须使用以下字段：

| Finding | 处理状态 | 修复位置 | 验证方式 | 复检关注点 |
|---------|----------|----------|----------|------------|

`处理状态` 只能是：`fixed` / `still-open` / `blocked` / `deferred` / `not-applicable`。

## 回写规则

### 回写 `docs/ark/plan.md`
- 根因导致原计划失效或需要调整执行顺序

### 回写 `docs/ark/tasks.md`
- 出现新的阻塞或诊断任务
- 某任务因 bug 需要重做 → 移回 Todo 或 Blocked

### 建议更新 `docs/ark/decisions.md`
- 修复路径引入了非平凡的技术取舍

### 建议更新 `docs/ark/spec.md`
- 修复后错误语义、验收标准、用户可感知行为或能力边界发生变化
- 原 spec 对失败行为、边界条件或非目标的描述被根因分析证明不成立

### 建议更新 `docs/ark/design.md`
- 修复改变异常转换、降级策略、接口契约、资源生命周期、并发/缓存/重试等设计机制
- 根因证明原 design 对模块职责、调用链或外部依赖的描述已过期

### 建议更新扩展文档
- 修复改变专题方案、接口契约、集成失败语义、数据源元信息或替身边界
- 根因证明扩展文档中的方案假设、契约描述或数据说明已过期

## 验证要求
- 必须区分症状与根因
- 必须区分假设与已确认事实
- 修复建议必须绑定验证思路（如何证明 bug 已修复）
- 若 bug 与真实依赖、真实数据或公开契约相关，验证思路必须区分真实验证与替身验证
- 来自外部 review gate 的 findings 必须保持修复边界：只修复“必须修复”项；“可延期”项应输出后续 task 建议或明确不处理
- 外部 findings 修复后，默认建议 `/ark:ark-review-gate recheck` 做定向复检，而不是重新扩大审查范围
- 外部 findings 未全部 `fixed` 或 `not-applicable` 前，不得建议直接进入 `/ark:ark-validate` 完结；必须先修复剩余项或说明 blocked / deferred 状态
- 外部 findings 修复后应为 `/ark:ark-test` 提供 finding 级测试目标，并为 `/ark:ark-review-gate recheck` 提供闭合摘要

## 停止条件
- 根因已足够清晰，可进入修复
- 或下一步诊断动作已被明确

## 固定输出格式

### 1. 症状摘要
### 2. 根因分析（区分假设 vs 已确认）
### 3. 影响范围
### 4. 修复方案（附验证方式）
### 5. 外部 findings 处理（如适用）
- 必须修复：
- 可延期：
- 不处理：
- Finding 闭合状态：
  | Finding | 处理状态 | 修复位置 | 验证方式 | 复检关注点 |
  |---------|----------|----------|----------|------------|
- 给 `/ark:ark-test` 的 finding 级测试目标：
- 给 `/ark:ark-review-gate recheck` 的闭合摘要：
- 建议复检：`/ark:ark-review-gate recheck`
### 6. 建议下一步（通常：`/ark:ark-test` 补充回归 → `/ark:ark-review-gate recheck`（如适用）→ `/ark:ark-validate`）
### 7. Artifact 回写
- `plan.md` / `tasks.md` / `decisions.md`：已更新 / 建议更新 / 无需更新
- `spec.md`：若发现漂移，建议 `/ark:ark-spec` 并说明原因；无漂移可省略
- `design.md`：若发现漂移，建议 `/ark:ark-design` 并说明原因；无漂移可省略
- 扩展文档：若发现漂移，建议 `/ark:ark-solution` 并说明原因；无漂移可省略

## 备注
不要在未理解失败模式前直接打补丁。根因不清楚时，先假设、再验证、再修复。
