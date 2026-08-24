# Nexgent 科研智能体运行时：最终定义

> 规范状态：**Normative Draft v0.1（2026-08-24）**
> 当前实现：Nexgent v0.5 只满足本规范的一部分；“已定义”不等于“已实现”。
> 实施证据与实时偏差见 [../research-runtime-progress.md](../research-runtime-progress.md)。

本文是 Nexgent 科研智能体方向的唯一产品与研究定义。后续接口、实现、测试、实验和论文主张
都必须能追溯到本规范中的 requirement ID；若代码与本文冲突，应显式修改规范或修复实现，
不能靠更换表述掩盖偏差。

文中的 **MUST / MUST NOT / SHOULD / MAY** 分别表示必须、禁止、推荐和可选。只有同时具备代码、
自动化测试与可复现实验输出，能力才可从 `PARTIAL` 晋升为 `CONFORMANT`。

## 1. 一句话定义

**Nexgent 是面向长周期科研代码与模拟的持久、证据治理型研究运行时。它控制科研智能体采用
什么搜索制度、哪些结论仍然有效，以及哪些恢复动作在当前状态下允许执行。**

英文定位固定为：

> **Nexgent is a persistent, evidence-governed research runtime for long-horizon
> scientific coding and simulation.**

Nexgent 的目标不是让模型“回答得像研究者”，而是让一个跨小时、跨进程、跨分支的研究过程
在失败、证据变化和环境漂移后仍然保持可判断的状态。

## 2. 服务对象与最终使用场景

### 2.1 主要用户

主要用户是拥有以下输入的计算科学、AI 或具身智能研究者：

- 一个代码仓库；
- 数据、模拟器或可执行实验环境；
- 可形式化的最低验收协议；
- 一组预算、权限和人类审批边界；
- 可能持续数小时到数天的研究目标。

用户提交的最终入口是 `ResearchSpec`：

```text
ResearchSpec
├── objective and research question
├── repository / data / environment refs
├── AcceptanceProtocol and EvaluationProtocol
├── BudgetPolicy and CapabilityPolicy
└── HumanAuthorityPolicy
```

Nexgent 的最终输出不是一句回答，而是可独立检查的 `ResearchRunBundle`：

```text
ResearchRunBundle
├── accepted claims and validity envelopes
├── experiment ledger, including negative results
├── branch and regime-decision history
├── code / data / environment / capability manifests
├── verification evidence
├── recovery and human-intervention trace
└── reproducibility and export manifest
```

### 2.2 三类第一方工作流

1. **科研代码搜索**：提出假设，修改实现，提交训练或评测作业，比较候选，识别搜索饱和并
   切换研究制度；
2. **科学工作流**：运行数据—模型—求解器—分析 DAG，把结论绑定到具体代码、数据、环境、
   文献和 validator，并在上游变化后选择性重跑；
3. **具身与仿真恢复**：把恢复意图绑定到当前对象、资源、affordance 和模拟器状态，先验证
   precondition / safety / postcondition，再批准不可逆动作。

首个正式交付边界仍是科研代码与可控模拟。真实机器人和湿实验设备是后续 Adapter，不是 v1
完成条件。

## 3. 系统边界

### 3.1 Nexgent MUST 拥有

- 持久 `ResearchRun`、Branch、Experiment、Attempt、Typed DAG、Event Log、Artifact Store；
- 版本化 Capability ABI、权限、按节点能力选择和副作用协议；
- 实验档案、候选选择、科研制度控制和条件化多智能体组织；
- Claim / Evidence / Validity 图、主动失效、记忆撤销和选择性重执行；
- 对齐 checkpoint、恢复计划编译、验证和人工审批边界；
- 可由独立进程校验的导出与重现 manifest。

### 3.2 通过 Provider / Adapter 接入

- 模型与推理服务；
- 论文数据库、文献全文与撤稿/版本信息；
- Git、代码索引、构建系统、调度器、实验跟踪器和对象存储；
- 科学求解器、模拟器、机器人中间件、传感器与实验设备。

外部系统的状态不能因“已经接入”而被假定为 Nexgent 已掌握。跨越
`WorkspaceBoundary / ExternalServiceBoundary / SimulatorBoundary /
PhysicalActionBoundary / HumanAuthorityBoundary` 的动作 MUST 产生 `EffectRecord`。

### 3.3 非目标

- 不训练或替代基础模型；
- 不做通用聊天助手、完整 IDE、通用多智能体框架或插件市场；
- 不把多角色提示、普通 RAG、文件快照、长期记忆或工具数量包装成核心创新；
- 不声称自动判断科学真理；Nexgent 管理可执行验证、证据依赖和适用范围；
- 不承诺回滚外部世界。不可逆状态只能验证、补偿、协调或交给人类；
- 不在缺少领域 validator 和安全 Adapter 时直接控制真实实验设备。

## 4. 最终端到端语义

给定 `ResearchSpec`，完整 Nexgent Run MUST：

1. 建立可重现 baseline，并固定目标、模型、能力、代码、数据、环境和评价版本；
2. 创建持久 Typed DAG，并按任务结构决定单 Agent 或 `ResearchTeam`；
3. 为每个节点按 goal、role、state、trust、effect 和当前 regime 解析最小能力集合；
4. 执行动作并记录 Event、Artifact、资源、成本、环境状态和 effect receipt；
5. 将每次实验无损写入 `ExperimentLedger`，再由独立 `CandidatePolicy` 选择候选；
6. 仅在证据依赖闭合且 validator 通过后把 `ScientificClaim` 标记为 `VALIDATED`；
7. 监测收益、重复、分支覆盖和失败，在 `EXPLOIT / DIVERSIFY / FALSIFY / EXPAND /
   ESCALATE` 之间作出可解释切换；
8. 上游代码、数据、文献、配置或环境变化时，使受影响 claim 与 memory 失效，并重跑最小
   受影响子图；
9. 发生故障时把 diagnosis 编译为满足当前状态、权限和副作用约束的 `RecoveryPlan`；
10. timeout 或结果未知时先验证 postcondition，再决定 retry；不可逆动作不能自动重放；
11. 在 fresh process 中继续同一个 Run，重建团队、预算、DAG、证据和 effect frontier；
12. 导出可独立验证的 `ResearchRunBundle`，使成功、结论和策略复用回落到原始证据。

## 5. 目标架构

```text
GUI / TUI / CLI
       │
NexgentRuntime / ResearchRuntimeFacade
       │
ResearchOrchestrator
├── RegimeController                 P1: search control
├── ResearchTeamScheduler
├── PersistentTypedDAGRunner
│   └── GoalController               existing inner task loop
│       ├── ValidatorRegistry
│       └── RecoveryCompiler         P3: action control
├── ClaimValidityService             P2: epistemic control
├── CandidatePolicy / ExperimentLedger
├── CapabilityRegistry / Resolver
└── CheckpointService / EffectLedger
       │
RunRecorder
       │
SQLiteRunStore + Content-addressed ArtifactStore
       │
Code · Data · Literature · Scheduler · Simulator · Robot
```

`NexgentRuntime` 仍是所有前端共享的 facade；`RunRecorder` 仍负责有序事实；
`SQLiteRunStore` 仍采用单写者 durable truth；`GoalController` 保留现有
`SPECIFY → EXECUTE → VALIDATE → DETECT → ATTRIBUTE → RECOVER → RERUN` 内层循环。

P1 在实验/分支边界运行，不塞进 `GoalController`；P2 是 event subscriber、claim gate 和
revalidation planner，不维护第二个调度器；P3 只编译和校验恢复计划，最终 commit 仍走统一
执行器。

控制优先级固定为：

```text
Human authority and safety > claim validity > search optimization
```

P1 无权越过 P2 判定的失效 claim、P3 判定的不允许动作、预算或审批边界。

## 6. 运行层级与一等契约

### 6.1 运行层级

```text
ResearchRun
└── ResearchBranch
    └── ExperimentRun
        └── RunAttempt
            └── WorkflowNode
```

- `ResearchRun`：用户提交的一次完整研究目标和权限边界；
- `ResearchBranch`：一种假设或方法路线；
- `ExperimentRun`：固定代码、数据、环境和评价协议下的可执行实验；
- `RunAttempt`：retry、resume 或 recovery 后的一次执行；
- `WorkflowNode`：Agent、Tool、Process、Simulator、Validator 或 Approval primitive。

现有 schema 1.0 的 `ExperimentRun` 不原地改变语义。它迁移为
`ResearchRun + default ResearchBranch + ExperimentRun`，新层级使用 schema 2.0 和显式 migrator。

### 6.2 契约目录

| ID | 契约 | 最小语义 |
| --- | --- | --- |
| `CON-001` | `ResearchSpec` / `ResearchRun` | 问题、目标、父分支、预算、权限和版本闭包 |
| `CON-002` | `ResearchBranch` / `ExperimentRecord` | 假设血缘、方法家族、固定评价与实验结果 |
| `CON-003` | `WorkflowNode` / `ResearchTask` | typed I/O、owner、依赖、预算、effect、validator、retry |
| `CON-004` | `CapabilityDescriptor` / `CapabilityBinding` | 稳定 ID、版本、Schema、错误、权限、effect、成本、健康和实际绑定 |
| `CON-005` | `ExecutionEvent` / `ArtifactRecord` | append-only 顺序事实、摘要、因果、数据、产物和责任关系 |
| `CON-006` | `EvaluationProtocol` / `CandidateDecision` | 指标/约束版本、成本、负结果、晋升和独立复现 |
| `CON-007` | `ScientificClaim` / `EvidenceRecord` | statement、scope、validity envelope、证据/反证、validator、状态 |
| `CON-008` | `ResearchTeam` / `DelegationRecord` | 角色、能力、局部预算、任务、租约、handoff 和责任血缘 |
| `CON-009` | `MemoryViewItem` | provenance、scope、版本、trust、TTL、适用条件和失效原因 |
| `CON-010` | `AlignedCheckpoint` | Agent、DAG、artifact、环境、资源、manifest、effect cursor 的一致切面 |
| `CON-011` | `EffectRecord` | target、class、请求摘要、幂等键、dispatch/commit/postcondition/compensation |
| `CON-012` | `RecoveryPlan` | diagnosis、目标、preconditions、动作 DAG、风险、审批、postconditions |
| `CON-013` | `RegimeDecision` | 输入信号、策略版本、旧/新 regime、置信度、预算、触发证据和后续收益 |

现有 `DependencyEdge` 继续表示执行依赖。Scientific support、contradiction 和 validity 使用独立
`ClaimEdge`，不能继续全部塞入自由字符串引用。`ToolDef` 保留为模型调用 Adapter，
`CapabilityDescriptor` 才是权威能力契约。

所有新契约 MUST：

- 有 schema version、严格反序列化和显式迁移；
- 使用稳定 ID，不用含义不明的自由字符串替代一等实体；
- 在持久化前验证，在导出后可由独立进程重新验证；
- 对影响重放的缺失版本和摘要 fail closed。

## 7. 系统不变量

| ID | MUST 始终成立 | 证明方式 |
| --- | --- | --- |
| `INV-001` | `SQLiteRunStore + ArtifactStore` 是运行事实源；Memory、GUI 和索引可重建 | 删除派生层后的重建摘要 |
| `INV-002` | 每个 durable entity 可解析到 Run、产生事件、执行者和输入依赖 | strict provenance closure |
| `INV-003` | 无 `VerificationResult(ACCEPT)` 不得进入 verified success | 状态机 property test |
| `INV-004` | `VALIDATED` claim 具有闭合依赖、scope 和 validator；stale claim 不得准入 | claim state × purpose matrix |
| `INV-005` | capability 冲突、不兼容或不健康绑定确定性拒绝 | ABI conformance suite |
| `INV-006` | 模型只看到节点所需 shortlist；完整 registry 不默认进入上下文 | resolver + context telemetry |
| `INV-007` | 结果未知的 effect 在 postcondition 检查前不得 retry | timeout-after-dispatch injection |
| `INV-008` | 不可逆动作遵守 proposal → durable approval → commit | effect lifecycle test |
| `INV-009` | checkpoint 恢复后 Run、DAG、artifact、环境和 effect frontier 一致 | crash matrix digest comparison |
| `INV-010` | CandidatePolicy 不得删除未晋升实验、失败、反例或拒绝分支 | ledger integrity test |
| `INV-011` | team task、handoff、message、预算和产物全部映射到 Run/DAG/Event | fresh-process team resume |
| `INV-012` | Run、Branch、Member、Experiment、Recovery 受同一层级硬预算约束 | concurrent budget ledger |
| `INV-013` | accepted result 固定代码、数据、环境、模型、prompt、capability 和 validator 版本 | manifest completeness gate |
| `INV-014` | 恢复动作绑定真实 target，满足当前 preconditions 并验证 postconditions | RecoverSpec conformance |
| `INV-015` | GUI、TUI、CLI 只调用共享 runtime，不各自实现 P1/P2/P3 | normalized frontend traces |
| `INV-016` | 安全/权限优先于 validity，validity 优先于 search policy | policy-conflict test |

## 8. 核心使能层

这些能力 MUST 实现和评测，但不单独作为主要研究贡献。

### 8.1 Capability ABI（`CAP-*`）

- `CAP-001`：稳定 namespace/name/version、input/output Schema、错误类型、permission、effect class、
  cost/latency、trust、资源、artifact 类型与 health check；
- `CAP-002`：同名、同 ID 不同内容和不兼容版本注册 MUST 失败；
- `CAP-003`：plugin / MCP / built-in 全部适配同一 ABI，并通过 conformance suite；
- `CAP-004`：load / unload / refresh 原子更新活跃 registry，历史 Run 保留绑定摘要；
- `CAP-005`：`CapabilityResolver` 按节点返回有理由、可审计的 shortlist；低置信度可扩大集合，
  不能退化为默认全量暴露；
- `CAP-006`：`EXPAND` 可触发能力缺口诊断，但新能力在验证和授权前不能执行。

### 8.2 Aligned checkpoint 与 effect-safe execution（`REC-*`）

- `REC-001`：`AlignedCheckpoint` 保存 `CON-010` 的完整一致切面；
- `REC-002`：在 node commit、branch fork、验证完成和 effect dispatch/commit 建立检查点；
- `REC-003`：effect class 至少区分 `PURE / IDEMPOTENT / REVERSIBLE / IRREVERSIBLE`；
- `REC-004`：timeout 或连接中断后 verify-before-retry，并使用幂等键和重复失败守卫；
- `REC-005`：恢复遵守 replay-or-fork；不可逆动作不能靠重新生成略有不同的请求绕过旧授权；
- `REC-006`：rollback、compensation、reconciliation、fork 和 escalation 有不同状态与证据。

### 8.3 Claim / Evidence 数据平面（`CLM-*`）

- `CLM-001`：一等区分 Claim、Evidence、Artifact、Validator、Environment、Code 和 Data；
- `CLM-002`：支持 `supports / contradicts / derived_from / valid_under / produced_by / supersedes`；
- `CLM-003`：claim 状态为 `UNVERIFIED / VALIDATED / STALE / CONTESTED / INVALIDATED / REJECTED`；
- `CLM-004`：允许矛盾、多版本与循环；“被记录”不等于“为真”；
- `CLM-005`：支持依赖闭包、局部视图、变更定位及 PROV-O / RO-Crate 导出映射。

### 8.4 ExperimentLedger 与 CandidatePolicy（`EXP-*`）

- `EXP-001`：每个实验记录 objective metrics、硬约束、验证、成本、regime、方法家族、版本和失败；
- `EXP-002`：评价协议在看到结果前固定；目标变化创建新版本，不改写历史；
- `EXP-003`：独立维护 `Champion / ParetoArchive / DiverseChallengers / NegativeArchive`；
- `EXP-004`：晋升要求独立重跑；regime 或 manifest 漂移后 champion 转为待复验；
- `EXP-005`：greedy 仅允许在 `EXPLOIT`；moonshot 有显式预算。

### 8.5 ResearchTeam（`TEAM-*`）

- `TEAM-001`：多智能体是条件化执行制度；强顺序节点只有一个 owner；
- `TEAM-002`：lead 负责 Run，manager 负责子 DAG，worker 负责节点；全部共享持久控制面；
- `TEAM-003`：支持模型、工具、文献视野、种子和上下文不同的异质分支；
- `TEAM-004`：区分组织并行与证据独立，支持 blind replication 和 proposer/verifier 隔离；
- `TEAM-005`：记录协调开销、重复率、分支差异、disagreement 和 error correlation。

### 8.6 可失效记忆（`MEM-*`）

- `MEM-001`：每条 memory 带 provenance、scope、版本、trust、TTL、regime 和失效条件；
- `MEM-002`：未经独立验证的猜测不能晋升；Agent 的成功声明不能自证；
- `MEM-003`：上游撤销后 retrieval rate 为零，且可从事实源重建；
- `MEM-004`：保存负结果、失败约束和已验证恢复 recipe；
- `MEM-005`：检索同时检查相关性、前提兼容性和 token budget。

### 8.7 Literature 与 Codebase Provider（`PROV-*`）

- `PROV-001`：Literature Provider 保存 query、数据库、时间、过滤、paper/version/chunk、原文位置；
- `PROV-002`：区分 primary evidence、secondary synthesis、Agent interpretation；同时检索支持、
  反对、更新与撤回，新证据默认 `UNVERIFIED`；
- `PROV-003`：Codebase Provider 建立绑定 commit 的模块、符号、调用、import、配置、测试、入口；
- `PROV-004`：按节点返回局部 ego-graph，支持增量更新、影响分析和旧依赖失效；
- `PROV-005`：回答回落到 paper claim 或 code symbol，最终正确性仍由 validator 决定。

## 9. 三个控制面与研究贡献

### 9.1 P1 — Regime-Aware Research Controller

`ResearchRegime = EXPLOIT | DIVERSIFY | FALSIFY | EXPAND | ESCALATE`。

P1 解决在线饱和检测与研究制度切换。控制器消费 accepted verification、P2 允许的 claim、
ExperimentLedger，以及 validated progress / token/time/GPU-hour、重复度、失败模式、分支覆盖、
结果方差、validator disagreement、capability gap、不可逆性、剩余预算和 human value-of-information。

第一版 MUST 使用规则/统计检测器；在建立校准实验前，未解释的学习式策略不得进入默认控制路径。
P1 不能直接操作 workspace 或 simulator，只产生可审计 `RegimeDecision` 和 `BranchPlan`。

核心新意是**在线饱和检测与 research-regime switching**，不是“使用多智能体”。

### 9.2 P2 — ClaimCI

P2 监听代码、数据、环境、文献和 validator 变化，改变 claim 状态，阻止失效结论进入 P1 或
候选晋升，撤销派生 memory，并创建最小 `RevalidationPlan`。

只有新的独立验证通过，claim 才能恢复 `VALIDATED`。P2 不选择研究方向，也不维护第二套 DAG。

核心新意是让 provenance 具有**运行时效力**：active invalidation、admission gate 和 selective
re-execution；被动记录不是贡献本身。

### 9.3 P3 — RecoverSpec

P3 把 `RecoveryIntent + StateSnapshot + AdmissibleActionSpace` 编译为 `RecoveryPlan`。它完成
target binding、Schema、precondition、resource、permission、risk 和 dry-run 检查；不可逆动作
拆成 proposal/approval/commit，执行后检查 postconditions。

P3 不判断整条研究路线是否值得继续，也不直接执行动作。无合法计划时返回 `ESCALATE`，或向
P1 发出 capability-gap / saturation signal。

核心新意是 **state-constrained recovery compilation**，不是把自由文本包进 JSON Schema。

### 9.4 三者闭环

```text
P1 chooses regime and branches
 → Team / DAG executes
 → Validators produce evidence
 → P2 updates claim validity
 → P1 computes progress only from admitted evidence

Execution fails
 → detect / attribute
 → P3 compiles and checks recovery
 → unified executor commits and checks postconditions
 → P2 updates affected claims
 → repeated recovery failure becomes a P1 signal
```

## 10. 验收证据矩阵

| Requirement | 必需证据 |
| --- | --- |
| `INV-001..002` | 重建前后摘要 + strict provenance closure report |
| `INV-003` | 状态机 property test 与非法跃迁报告 |
| `INV-004` | claim state × purpose 准入矩阵 + mutation suite |
| `INV-005..006` | capability conformance + resolver/context telemetry |
| `INV-007..009` | timeout/crash matrix + effect reconciliation + digest comparison |
| `INV-010` | attempt/negative-result retention report |
| `INV-011..012` | team resume trace + concurrent parent/child budget ledger |
| `INV-013` | version-closure manifest report |
| `INV-014` | valid/invalid recovery matrix + simulator fault campaign |
| `INV-015..016` | normalized frontend trace + policy precedence test |
| `P1-*` | frozen benchmark、static baselines、ablation 与 controller overhead |
| `P2-*` | change-injection matrix、false acceptance、rerun precision/recall/cost |
| `P3-*` | free-form / schema-only / state-constrained recovery comparison |

实现状态只能使用：

- `UNIMPLEMENTED`
- `PARTIAL`
- `CONFORMANT`
- `WAIVED_BY_ADR`

“字段存在”“演示可运行”或“测试未失败”不能单独证明 `CONFORMANT`。

## 11. 经核验的近邻工作与边界

- [Long-Horizon Autonomous Architecture Research](https://arxiv.org/abs/2608.01995) 报告约百次
  连续实验中的饱和墙、workflow-induced greedy search 与 action-surface expansion；它支撑 P1
  问题，但阶段转换由人类声明，不能直接证明在线 detector；
- [ScienceFlow](https://arxiv.org/abs/2608.14354) 已覆盖 recoverable executable state、
  re-anchoring 与 evidence-aware allocation；Nexgent 不能把普通可恢复状态作为主要创新；
- [Artifact-centered Claim-aware Observability](https://arxiv.org/abs/2608.18312) 与
  [PROV-AGENT](https://arxiv.org/abs/2508.02866) 说明 claim/artifact/provenance 是必要数据平面，
  但不能证明 provenance 自动提高科学正确性；
- [Verified Tool Calls](https://arxiv.org/abs/2608.02645) 支撑 postcondition、
  verify-before-retry 与幂等键；
- [ACRFence](https://arxiv.org/abs/2603.20625) 指出 restore 后重新生成不同请求会造成 semantic
  rollback attack，支撑 replay-or-fork 与 authority 不复活；
- [Future-House/paper-qa](https://github.com/Future-House/paper-qa) 可作为 Literature Provider
  的文献检索、来源和 contradiction workflow 接口参考；
- [OpenHands persistence](https://docs.openhands.dev/sdk/guides/convo-persistence) 可作为 event 与
  Agent state 持久化的工程对照；
- [W3C PROV](https://www.w3.org/TR/prov-overview/) 与
  [RO-Crate](https://www.researchobject.org/ro-crate/) 是外部互操作目标，不替代内部控制语义。

引用只支持其明确覆盖的结论。实现前必须阅读论文和代码，不以摘要、star 数或 README 宣传语
代替可复现证据；论文写作前按当时日期重新检索 related work。
