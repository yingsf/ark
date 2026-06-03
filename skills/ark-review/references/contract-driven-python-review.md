# Contract-driven Python Review

本文件承载 `/ark:ark-review` 的 Python 深度契约审查清单。执行 review 时默认读取并按适用性执行；若某项与本次变更无关，在报告中可压缩为“不适用”。

## 契约识别

先提炼本次实现必须满足的行为契约：

- 对外 API / CLI / 配置 / 文件格式 / 数据结构的名称、参数、返回值和异常语义
- 状态更新语义：replace、merge、atomic swap、rollback、失败保留旧值、部分失败隔离
- 数据隔离要求：deep copy、不可变快照、输入输出边界、内部 mutable 状态是否暴露
- 失败路径：校验失败、资源不可用、配置缺失、未找到默认范围、外部依赖失败
- 默认查询范围、缺省参数、空状态、fallback 行为
- 权限、租户、batch、version、环境、数据源等边界
- 排序、分页、过滤、去重、聚合等可观察语义
- 日志、安全、敏感信息输出和异常消息要求
- 后续模块会依赖的行为和完成信号

审查时优先判断代码是否真实满足契约，而不是只判断测试是否通过。

## 跨层口径一致性

必须检查同一个业务概念在上游、当前层、下游和测试中的定义是否一致。

重点检查：

- mapper / parser / profiler / service / repository / API 对同一状态值是否使用同一口径
- 质量指标、异常类型、去重状态、排序键、脱敏状态是否有单一事实源
- 是否把多个来源直接相加导致重复计数
- 是否只看 raw 状态而漏掉 anomaly / profile / canonical 中已定义的业务异常
- batch 级与 file 级、session 级与 message 级统计是否混用不同粒度
- 默认查询是否跨 batch、parser version、tenant、permission scope 或数据源混合数据
- 测试是否覆盖真实组合链路，而不是只构造单层假数据

危险信号：

- 上游使用一种异常状态，下游统计另一种状态
- repository 默认查询不限定范围，service 在无默认范围时传入空 scope
- SQL 排序和 service 层二次排序口径不同
- fake repository 行为和真实 repository 不一致

## fail-closed 默认行为

所有默认查询、缺省参数、空状态、配置缺失、未找到资源、无活跃版本等场景，必须检查是否 fail-closed。

重点检查：

- 未传 `batch_id`、`parser_config_version`、tenant、permission scope 时是否有明确默认范围
- 找不到默认范围时是否返回空结果或明确错误，而不是退化成全量查询
- 权限、租户、版本、批次、环境、数据源范围缺失时是否不会放大查询范围
- fallback 是否只作用于异常场景，并有显式标记，不会掩盖数据异常
- 空列表、空配置、`None` 状态是否会造成跨范围混合

危险信号：

- `if scope is not None` 才加查询条件，`scope is None` 时没有替代限制
- 默认 batch 不存在时继续查询 group / project / global 范围
- 配置缺失时使用过宽默认值
- 查询 API 默认返回最新任意记录，而不是返回明确 scope 的记录

## 状态与数据边界

重点检查：

- 构造器、setter、update 方法是否复制外部输入，避免外部引用污染内部状态
- getter / snapshot / cache 是否暴露内部 mutable 对象
- `frozen=True`、`Mapping`、tuple 等类型是否真的保证嵌套不可变
- deep copy、shallow copy、递归冻结的选择是否符合业务值类型
- 失败路径是否保持系统状态可预测，是否支持 rollback 或失败保留旧值
- 异常处理是否过宽、过窄、吞掉关键信息或泄露敏感信息
- async、线程、锁、连接池、文件句柄、后台任务等资源生命周期是否正确

典型陷阱：

- 表面不可变：对象 frozen，但内部 dict/list 仍可变
- 校验失败后部分状态已写入
- snapshot 返回内部引用
- 修复边界 case 时破坏主路径状态机

## 排序、去重、聚合专项

如果任务涉及排序、去重、聚合、统计、质量指标，必须专项审查。

排序检查：

- 主排序键、tie-breaker、fallback 是否与契约一致
- 时间缺失或解析失败是否只影响异常对象，不破坏正常对象排序
- SQL 排序与 service 层二次排序是否一致
- 是否有稳定 tie-breaker，例如 id
- 测试是否覆盖反向排序、同时间、缺失时间、重复键等反例

去重检查：

- confirmed duplicate 与 business duplicate candidate 是否区分
- 默认回放是否只隐藏契约规定可隐藏的重复
- duplicate candidate 是否保持可见并标记
- dedup scope 是否包含 parser version、tenant、batch 或其他必要边界

聚合检查：

- batch / file / session / message 等不同粒度是否混淆
- 指标是否重复计数或漏计
- 统计对象是事件数、消息数、行数还是唯一受影响对象数，是否明确
- 同一异常同时存在 raw 状态和 anomaly 记录时是否去重

## 安全输出审查

如果任务涉及配置、日志、报告、API、replay、异常样例、lineage，必须检查默认输出不泄露敏感信息。

重点检查：

- 是否返回完整 content、raw_record_text、raw_payload、连接串、密钥、token、password、secret、key
- 是否只返回 redacted_content、hash、安全引用、统计、schema keys 或脱敏摘要
- lineage 是否只含安全 id/hash，不含原文
- 日志、异常消息、测试快照和对象字符串化结果是否避免敏感信息
- 测试是否检查敏感原文不会出现在输出对象和日志中

## 测试真实性审查

测试通过但业务语义不对是 review 的重点风险。

必须检查：

- 主路径、失败路径、边界条件、状态不变性是否覆盖
- 是否有“修复前会失败、修复后会通过”的反例测试
- 测试是否验证行为契约，而不是私有实现细节
- fake / fixture / helper 的行为是否和真实 repository / service 一致
- 是否存在只断言函数被调用、对象能创建、happy path 通过的低价值测试
- 类型检查、lint、格式检查是否能发现测试未覆盖的问题
- 测试名称是否表达业务行为，失败时是否能定位问题

## 类型与运行时一致性

类型注解不能替代运行时行为审查。

重点检查：

- `Optional` 是否被正确处理
- `Any` 是否掩盖关键约束
- `Mapping` 是否真的只读
- pydantic / dataclass / attrs / TypedDict 是否真的被使用到边界校验
- 返回类型是否表达真实失败语义
- async 接口是否有真实 await 或明确接口统一理由

## Finding 判定

以下情况通常应进入 Findings：

- 明确违反任务契约或完成信号
- 运行时错误、状态污染、数据损坏、安全泄露或权限范围放大
- 默认查询或 fallback fail-open
- 修复一个问题时破坏核心主路径
- 测试通过但关键承诺行为没有被实现
- 测试缺口会让重要回归较容易漏掉

以下情况通常进入 Craftsmanship 或 Open Questions：

- 更好的命名、helper、结构整理，但当前不影响契约
- 风格偏好、局部可读性、轻度重复
- 缺少上下文才能判断的问题
