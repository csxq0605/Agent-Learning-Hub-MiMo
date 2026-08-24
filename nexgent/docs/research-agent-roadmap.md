# Nexgent 科研智能体交付路线图（2026-08）

> 本页只描述实施顺序与研究假设，不定义系统语义。
> 最终定义：[specs/research-runtime-spec.md](specs/research-runtime-spec.md)
> 评价协议：[specs/evaluation-protocol.md](specs/evaluation-protocol.md)
> 实时状态与偏差：[research-runtime-progress.md](research-runtime-progress.md)

## 1. 交付原则

1. 先固定契约、不变量和反证，再写实现；
2. 每个纵切必须同时覆盖权威契约、真实执行路径、持久化、导出和匹配范围的测试；
3. “字段存在”“demo 能跑”和“测试未报错”不等于语义成立；
4. P1/P2/P3 共用一个 Run/Event/Artifact 事实源，不各自生长数据库或调度器；
5. 使能能力认真实现、单独验收、进入消融，但不包装成研究 novelty；
6. 每次提交更新进度台账，显式比较设计与实际并关闭或新增 deviation；
7. README 只描述已经达到 `CONFORMANT` 的能力。

## 2. Milestone 总览

| 阶段 | 交付目标 | 依赖 | 关键完成证据 |
| --- | --- | --- | --- |
| M0 | Specification Lock | 当前 v0.5 审计 | 规范、评价协议、ADR、requirement 与偏差台账 |
| M1 | Runtime Kernel | M0 | Capability ABI、effect ledger、aligned checkpoint、schema migration |
| M2 | Enabling Research Plane | M1 | Claim/Evidence、ExperimentLedger、Team、MemoryView、Providers |
| M3 | P1 Regime Controller | M2 | 在线饱和检测、制度切换、静态基线与消融 |
| M4 | P2 ClaimCI | M2，使用 M3 trace | 主动失效、准入门、memory withdrawal、最小重执行 |
| M5 | P3 RecoverSpec | M1–M2 | state-constrained recovery、effect commit、simulator fault campaign |
| M6 | Integrated Reference Run | M3–M5 | 可公开复现的完整 ResearchRunBundle |

M1–M2 是系统底座；M3–M5 是研究控制面。顺序表达最小依赖，不要求后三项按论文顺序发表。

## 3. M0 — Specification Lock

### 已完成

- [x] 固定唯一定位：persistent, evidence-governed research runtime；
- [x] 固定 `ResearchRun → Branch → Experiment → Attempt → Node` 层级；
- [x] 固定 search / epistemic / action 三个控制面及其优先级；
- [x] 建立 requirement、不变量、里程碑和初始设计—实现偏差；
- [x] 建立可靠性、P1、P2、P3 和 integrated run 的评价协议草案；
- [x] 接受层级控制面与 CapabilityDescriptor 两项 ADR。

### 退出条件

- [ ] 添加 glossary 和 schema 2.0 字段草案；
- [ ] 完成 schema 1.0 → 2.0 migration ADR；
- [ ] 增加机器可校验的 requirement/evidence manifest；
- [ ] 运行并保存当前全量测试 baseline；
- [ ] 将 README 的“下一阶段”入口更新到新文档体系。

## 4. M1 — Runtime Kernel

M1 拆成四个独立纵切，按顺序关闭 `DIV-005/006/008/010`。

### M1-A Capability ABI 与原子 Registry

- [ ] 新增 provider-neutral `CapabilityDescriptor / CapabilityBinding /\n  CapabilityManifest`；
- [ ] `ToolDef` 保留为模型调用 Adapter，旧构造方式兼容；
- [ ] descriptor digest 使用 canonical metadata 和 canonical ID 排序，不 hash handler/加载顺序；
- [ ] registry 冲突时拒绝整个 candidate catalog，active snapshot 原子不变；
- [ ] built-in、plugin、MCP 通过统一 conformance suite；
- [ ] plugin/MCP lifecycle 使用 provider-scoped replace/remove，消除同名“第一个命中”；
- [ ] Run 持久保存实际 capability binding manifest。

验收：注册顺序无关 digest、snapshot generation、refresh 稳定性、坏 Provider 不部分注册、
同名多 server 可确定寻址、manifest 可导出并复算。

### M1-B Node-local Capability Shortlist

- [ ] 新增 `CapabilityRequirement / SelectionContext / SelectionResult`；
- [ ] 第一版使用确定性规则：exact ref → tag/precondition/trust/permission → rank/cap；
- [ ] prompt、API Schema、并发判定和 dispatch 使用同一个 immutable snapshot；
- [ ] 模型伪造调用 shortlist 外能力时，handler 不得执行；
- [ ] typed Agent node 使用明确 `AgentNodeExecutor` Adapter；
- [ ] node event 保存 selection reason、resolved refs 和 shortlist digest；
- [ ] resume 检测 capability drift，不能静默换新版。

验收：不同节点得到不同集合；运行中 refresh 不改变当前 Run；下一 Run 可见新版本；缺少绑定在
LLM 调用前 fail closed。

### M1-C Durable Attempt / Effect Ledger

- [ ] 新增 `WorkflowNodeAttempt / EffectRecord / RetryPolicy / CapabilityResult /\n  CapabilityError / PostconditionResult`；
- [ ] durable attempt 以 `run/workflow/node/input_digest` 计算重试预算，fresh process 不重置；
- [ ] effect 生命周期覆盖 prepared、running、succeeded、failed、outcome_unknown、compensated；
- [ ] PURE 可自动 retry；IDEMPOTENT 只用同一个 key；UNKNOWN 默认停止；
- [ ] timeout-after-dispatch 先运行 postcondition；
- [ ] REVERSIBLE 在 M1-D 前暂停；IRREVERSIBLE 不自动 retry；
- [ ] typed invoke 保留错误类别，legacy JSON-string execute 不参与安全重试。

验收：attempt history 不覆盖；crash 后剩余预算准确；不可逆 executor 只调用一次；postcondition
APPLIED 不重复调用；INCONCLUSIVE 进入 pause/escalation。

### M1-D Aligned Checkpoint、Rollback 与 Fork

- [ ] 新增 participant-based `AlignedCheckpoint / CheckpointPart / RestoreReport`；
- [ ] required parts 全部 capture 且 manifest durable 后才 COMMITTED；
- [ ] 边界覆盖 effect prepare/commit、node commit、verification、fork；
- [ ] workspace 首版只覆盖节点显式声明的 paths，并正确处理新增/删除 tombstone；
- [ ] simulator Adapter 分开定义 snapshot、restore、verify；
- [ ] process 使用 restart recipe，不声称恢复任意内存状态；
- [ ] lease 在恢复时重新获取，不复活旧 expiry；
- [ ] restore 全部 verify PASS 后 controller 才能进入 RERUN；
- [ ] fork 使用隔离 child workspace，并保留 checkpoint/branch lineage。

验收：多 crash-point fresh-process digest 一致、无重复 effect、失败 restore 不进入 RERUN、
parent workspace 不被 child 修改。

## 5. M2 — Enabling Research Plane

### M2-A Scientific Records

- [ ] schema 2.0 `ResearchSpec / ResearchRun / ResearchBranch / ExperimentRecord`；
- [ ] `EvaluationProtocol / MetricObservation / CandidateDecision`；
- [ ] `ScientificClaim / EvidenceRecord / ClaimEdge / ValidityEnvelope`；
- [ ] 独立 PROV-O / Workflow Run RO-Crate export mapping；
- [ ] strict provenance、version closure 与 negative-result retention verifier。

### M2-B ExperimentLedger

- [ ] 全量保留尝试、失败、反例、方法家族、成本和评价版本；
- [ ] CandidatePolicy 分离 `Champion / Pareto / DiverseChallengers / NegativeArchive`；
- [ ] champion 绑定 evaluator/version/regime，并经独立重跑晋升；
- [ ] evaluator 或 manifest 变化后转为待复验；
- [ ] greedy 只用于 EXPLOIT，moonshot 有独立预算。

### M2-C ResearchTeam 与硬预算

- [ ] team/member/task/delegation/handoff 映射到 Run/DAG/Event；
- [ ] 默认单 Agent，只在可分解、近似独立或需要对抗验证时 spawn；
- [ ] 单写者协调器、隔离 workspace、merge gate 和 lease；
- [ ] Run/Branch/Member/Experiment/Recovery 共享父子预算树；
- [ ] 执行期 token/cost/time 超限确定性停止。

### M2-D Memory 与 Provider

- [ ] MemoryView 从 Event/Artifact/Evidence 派生并可重建；
- [ ] episodic 与 procedural memory 分层，程序规则需多次独立验证；
- [ ] evidence 撤销后相关 memory retrieval rate 为零；
- [ ] Literature Provider 保存 statement-to-source、查询和版本；
- [ ] Codebase Provider 返回绑定 commit 的局部 symbol graph；
- [ ] Provider 输出只能生成 evidence candidate，不能自证 claim。

## 6. M3 — P1 Regime-Aware Research Controller

### 研究假设

与 greedy、静态多智能体、固定多样性和 re-anchor 相比，在线识别收益递减、重复失败和
capability gap，并在五种 research regime 间切换，可以提高固定预算下的
`validated progress / cost` 和 saturation escape rate。

### 实现

- [ ] progress、重复度、失败模式、分支覆盖、disagreement、capability-use telemetry；
- [ ] 规则/统计 saturation detector 与校准集；
- [ ] `EXPLOIT / DIVERSIFY / FALSIFY / EXPAND / ESCALATE` 状态机；
- [ ] 异质 branch plan、最小差异约束和 moonshot budget；
- [ ] transition observation、decision、预算变化与后续收益全部持久化；
- [ ] 按评价协议完成 baselines 和消融。

不能采用的主张：“多 Agent 更强”“保持多样性即可”。贡献必须落在在线检测和制度切换。

## 7. M4 — P2 ClaimCI

### 研究假设

与全量重跑、仅 hash cache 和被动 provenance 相比，主动 claim invalidation 可以显著降低
stale-claim false acceptance，并以更小工作流闭包恢复有效性。

### 实现

- [ ] claim admission gate；
- [ ] code/data/environment/literature/evaluator change ingestion；
- [ ] validity-envelope diff 与失效传播；
- [ ] stage/memory/candidate withdrawal；
- [ ] minimal revalidation planning；
- [ ] mutation matrix、误导证据和“正确答案/错误机制”实验。

贡献是 provenance 的运行时效力，不是记录一张图。

## 8. M5 — P3 RecoverSpec

### 研究假设

与自由文本和 Schema-only 恢复相比，把 recovery intent 绑定到实时 target、resource、
precondition、effect 和 simulator state，可以减少 diagnosis-correct-but-action-invalid、
unsafe effect 和重复动作。

### 实现

- [ ] `RecoveryIntent / AdmissibleActionSpace / RecoveryPlan`；
- [ ] target、resource、permission、precondition、risk 和 dry-run gate；
- [ ] effect transaction 与 postcondition；
- [ ] restore simulator、retry idempotent、compensate、replan-from-observation、safe-stop 等明确模式；
- [ ] 先在科学软件和模拟器 fault campaign 验证；
- [ ] 具身 Adapter 同时管理 controller state 与 environment/physics state；
- [ ] 真实世界只允许补偿、重新观测后重规划或安全停止，不使用“物理回滚”措辞。

## 9. M6 — Integrated Reference Run

选择一个可公开复现的科学代码或模拟项目，必须包含：

- 冻结 ResearchSpec、EvaluationProtocol 和 baseline；
- 多分支搜索与一次有证据的 regime transition；
- upstream change → claim/memory invalidation → selective replay；
- 一次 checked recovery 与 postcondition；
- 一次 process kill / fresh resume；
- 完整 ExperimentLedger、负结果和人类介入；
- ResearchRunBundle 与独立 verifier 输出。

该运行包才是首页宣称最终形态能力已经成立的依据。GUI 截图、功能 demo 和单个单元测试不能替代。

## 10. 当前最近工作

1. 完成 M0 剩余文档与 baseline；
2. 实现 M1-A Capability ABI；
3. 对照进度表复审，不把 descriptor 字段存在误报为 runtime binding 成立；
4. 实现 M1-B shortlist 并证明 prompt/schema/dispatch 一致；
5. 再进入 effect ledger 与 aligned checkpoint。

近邻论文、开源实现及其主张边界维护在最终规范与评价协议中；引入实现前应再次核验上游代码
版本和许可证。
