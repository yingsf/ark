---
name: ark-handoff
description: |
  生成面向未来恢复的阶段总结，使下一次继续工作时可以快速理解当前状态。
  触发时机：长任务暂停前、多阶段任务切换前、当前会话即将结束时。
  关键词：交接、handoff、会话结束、暂停、总结进展、恢复点、下次继续。
version: "1.0"
---

# /ark-handoff

## 目标
生成一个面向未来恢复的阶段总结，使下一次继续工作时可以快速理解当前目标、已完成内容、剩余问题与推荐路径。

## 前置建议
- 建议先执行 `/ark:ark-validate` 完成验证，再生成交接文档

## 适用场景
- 长任务暂停前
- 多阶段任务切换前
- 当前会话即将结束
- 希望降低下次恢复成本

## 不适用场景
- 任务极小且已彻底完成
- 当前状态过于混乱，应先 `/ark:ark-sync`
- 还没有任何可总结进展

## 输入
- 当前任务目标、`docs/ark/plan.md`、`docs/ark/tasks.md`、`docs/ark/validation.md`、当前代码与文档状态
- `docs/ark/handoff.md` 中已有 External Review Gate 记录，外部审查 pending batch 或 findings 状态（如有）
- 项目画像、核心命题与不变量、扩展文档索引和真实性锚点状态（如存在）

## 输出
- 当前目标、当前阶段判断、已完成内容、未完成内容、风险/阻塞、推荐下一步、关键文件列表
- Artifact 和扩展文档可信度、真实性锚点状态、下一次必须继承的结论
- External Review Gate 状态：pending task、batch 范围、外部审查状态、Finding 闭合状态和下一步（如采用跨智能体审查）

## 相关 Artifact
- `docs/ark/handoff.md`

## 工作流
1. 判断当前阶段（澄清/规划/实现/验证/收尾）。
2. 只写真实完成的内容，不写「本来打算做」的内容。
3. 重点列出恢复后真正还需要推进的事项。
4. 若后续恢复时可能踩坑，优先写在风险与阻塞里。
5. 推荐下一步应尽量具体。
6. 记录扩展文档可信度和真实性锚点状态，尤其是仍为替身的依赖、数据或契约。
7. 若存在 external review pending batch、findings-imported 或 recheck-pending，必须记录 External Review Gate 状态，避免下次恢复时误把任务当作可 Done。`findings-imported` 且未修复时，下一步应是 `/ark:ark-debug`；已修复但未复检时，下一步应是 `/ark:ark-review-gate recheck`；passed 但 validation 未记录 evidence 时，下一步应是 `/ark:ark-validate`。
8. 提炼下一次必须继承的结论：核心命题与不变量、validation 未覆盖项、已定 decisions、不要重复讨论的问题。
9. 列出关键文件帮助快速恢复上下文。

## 验证要求
- handoff 必须与当前真实状态一致
- 不应假装「所有事情都很清楚」
- 若当前状态本身不可信，应先建议 `/ark:ark-sync`
- 不得把 mock/fake/in-memory/合成数据状态写成真实闭环完成
- 不得修改 `docs/ark/handoff.md` 以外的核心 Artifact

## 推荐策略
- 实现基本完成但未验证 → 推荐 `/ark:ark-validate`
- plan / tasks 与代码状态脱节 → 推荐 `/ark:ark-sync`
- 扩展文档或真实性锚点状态不可信 → 推荐 `/ark:ark-sync`
- 还有明确实现项未完成 → 推荐 `/ark:ark-implement`
- 存在 external review pending / package-prepared → 推荐 `/ark:ark-review-gate prepare`
- 存在 findings-imported 且未见 Finding 闭合状态 → 推荐 `/ark:ark-debug`
- 存在 findings-imported 已修复或 recheck-pending → 推荐 `/ark:ark-review-gate recheck`
- 外部审查 passed 但 validation 未记录 evidence → 推荐 `/ark:ark-validate`

## 固定输出格式

### 1. 当前目标
### 2. 当前阶段
### 3. 已完成
### 4. 未完成
### 5. 风险 / 阻塞
### 6. 下一次必须继承的结论
- 核心命题与不变量：
- 当前真实闭环状态：
- validation 未覆盖项：
- 已定 decisions：
- 不要重复讨论的问题：
### 7. Artifact 信任状态
### 8. 扩展文档信任状态
### 9. 真实性锚点状态
### 10. External Review Gate
- Gate 结论：
- Pending task：
- Batch 范围：
- 外部审查状态：
- Finding 闭合状态：
- 下一步：
### 11. 恢复顺序
### 12. 推荐下一步
### 13. 推荐 Skill
### 14. 恢复提示

## 备注
handoff 的核心价值是「未来继续时不用重新想一遍现在发生了什么」。
