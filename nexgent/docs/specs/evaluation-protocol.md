# 科研运行时评价协议

> 状态：Pre-registration Draft v0.1（2026-08-24）
> 规范：[research-runtime-spec.md](research-runtime-spec.md)

本协议规定“如何证明实现与研究主张成立”。具体 task manifest、随机种子、预算和阈值必须在
第一次查看正式结果前冻结并提交；结果出现后不得通过改指标、删失败任务或更换 evaluator
修饰结论。

## 1. 通用规则

- 每个实验绑定不可变 `EvaluationProtocol ID`、代码/数据/环境/模型/capability/validator 摘要；
- 所有 attempt、失败、超时、人工介入和被淘汰分支进入 ExperimentLedger；
- 优先使用 paired design：相同任务、seed、初始状态和预算比较策略；
- 报告 task-level 分布、bootstrap confidence interval 和逐任务结果，不只报告均值；
- 区分系统成功、科学 validator 通过、claim admission、恢复成功和最终最好分数；
- controller、检索、团队协调、验证、checkpoint 自身的 token、wall time、GPU-hour 和存储开销
  必须计入；
- benchmark 不覆盖的范围不得外推；alpha 项目或 README 宣称不算 baseline 结果。

## 2. M1 可靠性协议

### Capability ABI

场景：同名不同实现、同 ID 不同 descriptor、版本不兼容、health 失败、Schema 不合格、
无权限、step-local tool 缺失和恶意相似描述。

指标：

- registration conflict rejection；
- conformance pass/fail precision；
- capability retrieval recall；
- LLM selection accuracy；
- execution success；
- shortlist 大小与 context token；
- unauthorized invocation 数。

比较：当前全量 `ToolRegistry`、固定 top-k、Nexgent resolver。

### Effect 与 checkpoint

fault matrix 至少覆盖：

- dispatch 前 crash；
- dispatch 后、响应前 timeout；
- effect 已发生但 receipt 丢失；
- postcondition 延迟可见；
- checkpoint 后 request 被模型改写；
- reversible / irreversible / unknown 元数据；
- process kill 后 fresh-runtime resume；
- workspace、DAG、artifact、environment 或 simulator digest 不匹配。

指标：

- duplicate / lost / unauthorized effect；
- clean success；
- recovered state digest agreement；
- orphan lease/task；
- unsafe automatic retry；
- replay / fork / compensate / escalate 的正确分类；
- recovery latency 与存储开销。

禁止使用 `exactly-once` 作为结论，除非作用域和外部系统共同提供可证明语义。

## 3. P1 协议

### 基线

1. 单 Agent greedy commit-or-discard；
2. 静态同质多 Agent；
3. 固定多样性分支；
4. live/archive re-anchor；
5. Nexgent Regime Controller。

### 任务

候选池包含 MLE-Bench 子集、FIRE-Bench 子集和至少一个公开可复现科学模拟任务。正式实验前
必须冻结：

- task IDs 与排除理由；
- 每任务 seed；
- wall-clock、token、GPU 和并行预算；
- evaluator 版本；
- 允许的人类介入；
- 模型与 capability manifest。

### 指标

- `validated_progress / cost`；
- saturation escape rate；
- time-to-validated-recovery；
- 重复/无效实验比例；
- 方法家族和证据来源覆盖；
- false regime transition；
- human interventions；
- controller 与 coordination overhead。

必须消融：无多样性约束、无 capability-gap signal、无 negative archive、无 moonshot budget、
始终多智能体、始终 EXPLOIT。

## 4. P2 协议

mutation matrix 至少包含：

- code symbol / dependency / build flag；
- data content / schema / split；
- environment / library / hardware；
- simulator model / controller / seed；
- literature version / retraction / contradiction；
- evaluator / threshold / acceptance protocol；
- memory poisoning 与上游 evidence revocation。

比较：全量重跑、仅 hash cache、被动 provenance、ClaimCI。

指标：

- stale-claim false acceptance；
- valid-claim false rejection；
- invalidation detection latency；
- affected-subgraph precision / recall；
- minimal rerun 节点数、成本与 wall time；
- stale memory retrieval rate（目标 0）；
- 恢复到 VALIDATED 的独立证据覆盖率。

## 5. P3 协议

比较：自由文本恢复、Schema-only、state-constrained RecoverSpec。

fault campaign 至少包含 invalid target、precondition failure、resource missing、permission denied、
timeout-after-dispatch、partial effect、simulator state/version mismatch、碰撞/安全边界和真实世界
不可回滚替身场景。

指标：

- admissible-plan precision / recall；
- recovery success；
- diagnosis-correct-but-action-invalid；
- duplicate / unsafe / unauthorized effect；
- postcondition false acceptance；
- compensation / reconciliation / human handoff；
- time、token 和 simulator-check overhead。

## 6. Integrated Reference Run

最终 reference run 必须公开：

- 冻结 ResearchSpec 与 EvaluationProtocol；
- baseline 与至少两个异质分支；
- 一次有证据的 regime transition；
- 一次 upstream mutation → claim/memory invalidation → selective replay；
- 一次 recovery compilation 与 postcondition；
- 一次 process kill / fresh resume；
- 完整 ResearchRunBundle 和独立 verifier 输出。

只有该运行包和全量协议证据通过后，首页才能把相应最终能力写成“当前提供”。

## 7. 待冻结项

以下不是实现阻塞，但在正式 benchmark 前必须从 `TBD` 变为固定值：

- task manifest 和合法排除条件；
- seed 数与统计置信区间方法；
- 每类任务预算；
- validated-progress 的领域归一化；
- saturation detector 的阈值和校准集；
- claim mutation 的生成与人工核验规则；
- simulator / embodied reference environment；
- hardware 与 provider 版本；
- artifact retention 与匿名化策略。
