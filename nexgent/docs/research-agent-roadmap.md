# 科研智能体路线图（2026-08）

> 状态：规划中。本页描述待研究、待验证和待实现的方向，不代表当前版本已经提供这些能力。

Nexgent 当前定位是面向长周期科研代码与模拟任务的持久、可追踪、验证驱动 Coding
Harness。下一阶段分成两条相互配合但必须明确区分的路线：

1. **能力内化**：补齐能力契约、恢复一致性、科学证据、实验档案、可失效记忆、多智能体
   组织、文献研究和代码库建模，使它们成为 Harness 的一等能力；
2. **研究创新**：围绕科研过程的搜索饱和、结论失效和恢复动作可执行性，提出新的运行时
   定义、控制机制和可复现实验。

这些底座能力本身不作为主要研究贡献；它们共同服务于科研制度控制、结论有效性管理和
受状态约束的恢复。

## A. P0：核心使能能力与现有实现差距

本节不是另一组平行的研究题目，而是 P1–P3 共同依赖的科研运行时。原则是：**认真实现、
单独验收、进入消融，但不把已有通用能力本身包装成主要创新。**

### A0. 当前实现审计

Nexgent 已经具备可复用的骨架，但若要支撑科研智能体研究，若干“字段存在”和“运行时语义
成立”之间的缺口必须先补齐：

| 现有基础 | 当前缺口 | P0 收敛目标 |
| --- | --- | --- |
| `SubAgent` 已支持隔离会话、步骤/时长限制、工具过滤、并行与 pipeline；bare 模式跳过项目记忆，活跃 Run 中的事件可被记录 | 累计 token/cost 预算并非执行期硬约束；team task、handoff 和成员关系仍是进程内状态 | 所有团队实体、硬预算、任务和产物进入持久 Run/DAG/Event Log |
| `ToolRegistry` 与 `PluginManager` 已能注册、发现工具 | 同名工具可静默覆盖；模型侧会看到全部已注册 Schema；插件安装/卸载未形成确定性的活跃注册表刷新 | 稳定 ABI、冲突拒绝、生命周期刷新和按节点动态 shortlist |
| 已有 `CheckpointManager`、`max_retries`、`checkpoint_id` 与 recovery contracts | 检查点主要是文件快照；retry/checkpoint 字段尚未贯通持久执行器；rollback 没有统一恢复 Agent、DAG、环境和副作用 | aligned checkpoint、effect-safe retry 和可验证恢复 |
| 已有 `ExperimentRun`、`WorkflowNode`、`DependencyEdge`、`ArtifactRecord`、`RecoveryAction` 等持久契约 | 已有执行、因果、恢复和验证边，但引用端仍是通用字符串；缺少一等 Claim/Evidence/Environment 节点及 `supports`、`contradicts`、`valid_under`、`supersedes` 等认识论语义 | 类型化 Claim/Evidence/Artifact/Validator 图 |
| `MemoryStore` 已提供带粗粒度类型元数据的文件记忆；`RecoveryStrategy` 已有窄域的证据晋升和失败降权 | 一般记忆仍缺少 provenance、scope、版本、自动检索和上游撤销；恢复策略不能替代通用科研记忆层 | provenance-backed、scoped、versioned、invalidatable memory |
| `SQLiteRunStore` 已持久记录运行、失败证据、诊断、恢复和验证结果 | 缺少统一 objective-metric 契约、候选晋升策略、Champion/Pareto/DiverseChallengers 和结构化可查询的 NegativeArchive | 在现有 store 上构建 `ExperimentLedger` 视图与独立 `CandidatePolicy` |

### A1. Capability ABI 与动态能力面

目标不是把更多插件直接暴露给模型，而是建立可复现、可审计、可按需激活的能力契约。

- [ ] 统一能力命名空间、版本、输入输出 Schema、错误语义、权限和健康检查；
- [ ] 为每项能力声明前置条件、effect class、成本、延迟、信任级别、资源要求和产物类型；
- [ ] 注册时确定性拒绝同名或不兼容能力，禁止因仓库尾名或短名称静默覆盖；
- [ ] install / load / unload 后原子刷新活跃 registry，并锁定历史 Run 所用版本；
- [ ] 所有能力通过最小 conformance suite 后才可调度；
- [ ] registry 保存完整能力集合，模型每个 `WorkflowNode` 只看到按 goal、role、state、trust
  和 regime 生成的动态 shortlist；
- [ ] 低置信度时允许扩大 shortlist；“能力缺口诊断”和自动发现仅作为 Experimental 路径。

验收指标：冲突拒绝率、版本重放成功率、tool retrieval recall、模型选择准确率、执行成功率、
上下文节省和未授权副作用数。

### A2. Event Log、对齐检查点与 effect-safe retry

checkpoint 不能只恢复聊天记录或工作区文件，而要形成科研执行状态的一致性协议。

- [ ] 同步保存 Agent/session、controller、ResearchRun、DAG 游标、artifact digest、环境/进程/
  模拟器状态、资源租约、已提交/未提交副作用以及 capability/model/version manifest；
- [ ] 在 node commit、外部副作用前后、验证完成和 branch fork 建立语义检查点；
- [ ] 将动作显式划分为 `PURE`、`IDEMPOTENT`、`REVERSIBLE`、`IRREVERSIBLE`；
- [ ] timeout 后先执行 postcondition verification，再决定 retry；
- [ ] 可重试调用必须使用 idempotency key，并设置次数、预算和重复失败守卫；
- [ ] 可逆动作提供 rollback，不可逆动作只能 compensation、reconciliation 或人工审批；
- [ ] 支持从 checkpoint fork 新分支，并与依赖图结合选择性 replay。

验收条件：在多组 crash-point fault injection 下，恢复后的 Run、DAG、artifact 和环境摘要一致，
不存在重复外部副作用、孤儿租约和无限重试。

### A3. 类型化 Claim/Evidence 基础图

图本身是 P2 的数据平面；P2 的创新是赋予它主动失效与选择性重验证的运行时语义。

- [ ] 一等区分 `Claim`、`Evidence`、`Artifact`、`Validator`、`Environment`、`Code` 和 `Data`；
- [ ] 定义 `supports`、`contradicts`、`derived_from`、`valid_under`、`produced_by` 等具体边；
- [ ] `VALIDATED` claim 必须绑定 validator，并拥有闭合、可追踪的上游依赖；
- [ ] 允许矛盾证据、循环和多版本并存，不能把“已记录”误判为“为真”；
- [ ] 支持 validity envelope、内容摘要、分支血缘、validator 独立性和局部物化视图；
- [ ] 置信传播、因果边或概率关系在完成校准实验前不得进入核心控制路径。

验收指标：Schema 完整性、依赖闭包率、注入变化下的边定位 precision/recall、存储和查询开销。

### A4. ExperimentLedger 与 CandidatePolicy

保留 best-so-far 是安全底线；only-best-survives 会把长期研究退化成贪心 hill climbing。

- [ ] 永久记录所有实验，包括负结果、失败原因、约束、代码/数据/环境版本、成本、资源、
  适用 regime、验证状态和 objective metrics；
- [ ] 用独立 `CandidatePolicy` 管理 `Champion`、`ParetoArchive`、`DiverseChallengers` 和
  `NegativeArchive`，不删除未晋升实验；
- [ ] evaluator 与指标版本在看到结果前固定，目标改变时创建新评价版本而非改写历史；
- [ ] 候选须经独立重跑才能晋升；代码、数据、硬件或任务 regime 变化后重新验证 champion；
- [ ] 将复现性、机制验证、成本、不确定度和方法家族覆盖纳入多目标选择；
- [ ] 为 moonshot 预留显式预算；greedy policy 只允许在 `EXPLOIT` 中使用。

验收指标：false-promotion rate、top-result replication rate、Pareto coverage、方法家族覆盖度和
validated progress / cost。

### A5. ResearchTeam：条件化多智能体执行平面

目标是把 lead / manager / worker 内化到持久 `ResearchRun`，而不是维护第二套任务状态机。
多智能体只在任务可分解、证据可独立或当前 regime 需要时启用；强顺序的有状态节点保持单一
owner。

- [ ] 定义 `ResearchTeam`、成员角色、父子关系、能力、局部预算、租约和取消语义；
- [ ] Team Lead 对完整 Run 负责，Manager 管理子 DAG 和研究分支，Worker 执行具体节点；
- [ ] team task、消息、委派、交接、shutdown 和产物全部映射到 DAG、Event 与 Artifact；
- [ ] 支持不同模型、工具、文献视野、随机种子和上下文的异质分支；
- [ ] 区分组织并行与证据独立，支持 blind replication 与 proposer/verifier 隔离；
- [ ] 记录 coordination overhead、重复劳动率、分支差异度、disagreement 和错误相关性；
- [ ] 所有 Shell、作业提交和外部副作用继续经过统一权限、预算与审计管线。

验收条件：fresh process 能恢复团队、任务依赖、成员状态和预算；crash injection 后没有孤儿
任务或重复 commit；每项产出均可追溯到 Run/Node/Agent/输入证据。

### A6. 来源可追踪、可失效的记忆

`Event Log + Artifact + Evidence` 是 source of truth；Memory 只是可重建、可压缩、可失效的
派生视图，不能成为第二套事实来源。

- [ ] 每条 memory 带 provenance、scope、创建版本、适用 regime、信任级别、TTL 和失效条件；
- [ ] 隔离 session、project、branch、team 和 global scope；
- [ ] 未验证猜测不得晋升到稳定层，Agent 也不能仅凭自己的成功声明完成 promotion；
- [ ] 上游证据撤销后，相关 memory 立即退出 retrieval，并可由原始事件重新构建；
- [ ] 保存负结果、失败约束和已验证恢复 recipe，减少等价死路的重复探索；
- [ ] 检索同时检查语义相关性与前提兼容性，并服从强制 token budget。

验收指标：grounded retrieval precision、撤销后 retrieval rate（目标为零）、压缩率、token 开销、
跨分支泄漏率和避免重复实验的比例。

### A7. LiteratureEvidenceProvider 与 CodebaseModelProvider

二者必须是不同的 Provider，而不是混成一个通用 RAG 工具。

**LiteratureEvidenceProvider**

- [ ] 定义 `PaperArtifact`、`LiteratureClaim`、`CitationEdge` 和 `QuerySnapshot`；
- [ ] 保存检索式、来源、时间、版本、排序/过滤过程、paper ID、chunk 与原文位置；
- [ ] 区分 primary evidence、secondary synthesis 和 Agent interpretation；新证据默认
  `UNVERIFIED`；
- [ ] 同时检索支持、反对、更新与撤回信息，并允许查询重放和漂移报告；
- [ ] 文献版本或可信状态变化时，使下游 claim 和 memory 可被失效。

**CodebaseModelProvider**

- [ ] 建立绑定 commit 的模块、符号、调用、import、配置、测试、入口和构建目标索引；
- [ ] 按当前节点返回受预算约束的局部 ego-graph，而不是把整个仓库塞入上下文；
- [ ] 将代码变更连接到实验、artifact、validator 与失败栈；
- [ ] 支持增量重建、变更影响分析、最小相关代码选择和旧依赖失效；
- [ ] fresh process 可以恢复同一 commit 的结构快照。

两类 Provider 的自然语言输出都必须回落到具体 paper claim 或 code symbol；最终正确性分别由
证据验证器与构建、测试、科学 validator 决定。

## B. 研究创新

### P1. Regime-Aware Research Controller

暂定题目：**Nexgent-RC: Regime-Aware Control for Long-Horizon Autonomous Research**。

#### 研究问题

系统能否在线识别科研路线已经进入收益递减或结构性饱和，并在局部优化、异质分叉、主动
反证、能力扩展和人类介入之间切换，以更少算力和人类干预获得更多已验证进展？

#### 核心定义

在现有 `SPECIFY → EXECUTE → VALIDATE → DETECT → ATTRIBUTE → RECOVER → RERUN`
任务闭环之上，增加研究策略层 `ResearchRegime`：

- `EXPLOIT`：沿当前最优路线做局部、低风险改进；
- `DIVERSIFY`：启动方法、代码结构或证据来源显著不同的并行分支；
- `FALSIFY`：优先生成反例、机制验证和 regime-shift tests；
- `EXPAND`：在证据表明 action surface 不足时启用新工具、适配器或成员类型；
- `ESCALATE`：不可逆、高不确定或高价值分叉交给人类决策。

任务状态回答“当前执行到哪里”；Research Regime 回答“下一段研究应采用什么搜索制度”。

#### 在线信号

- [ ] 单位 token、时间和 GPU-hour 的 validated-progress 斜率；
- [ ] 最近假设、补丁、配置与实验结果的语义/结构相似度；
- [ ] 同类失败、同类算子和重复实验的比例；
- [ ] 分支覆盖度、结果方差和 validator disagreement；
- [ ] 已知但未使用能力与当前阻塞类型的匹配度；
- [ ] 不可逆性、剩余预算和请求人类的预期价值。

#### 控制与组织

- [ ] 实现可解释的 regime detector，先从规则/统计版本开始，不依赖额外训练；
- [ ] 为不同 regime 定义预算、最大并行度、退出条件和审批策略；
- [ ] 用 `ResearchTeam` 实例化异质研究分支，而不是复制同一个 Agent 多次；
- [ ] 为 DIVERSIFY 定义最小差异约束，例如方法家族、代码路径、文献祖先或验证策略；
- [ ] 为 moonshot 分支保留显式预算，避免始终被短期收益淘汰；
- [ ] 将 regime 转换、触发证据和后续收益写入 Run Trace，允许离线反事实评估。

#### 最小实验

比较以下控制策略：

1. 单智能体贪心 commit-or-discard；
2. 静态同质多智能体并行；
3. 固定多样性搜索；
4. 基于历史状态的 re-anchor；
5. Nexgent 动态 Research Regime Controller。

候选任务包括 FIRE-Bench 子集、MLE-Bench 任务，以及可复现的长周期架构或科学模拟任务。

主要指标：

- [ ] best validated progress / GPU-hour；
- [ ] saturation escape rate 与 time-to-recovery；
- [ ] 重复或无效实验比例；
- [ ] 有效假设家族覆盖度；
- [ ] 达到目标所需人类介入次数；
- [ ] 动态控制器自身的 token、时间和并行资源开销。

#### 创新边界

贡献不能写成“使用多智能体提高科研表现”或“保持假设多样性”。关键贡献必须是：**面向
完整科研工作流的在线饱和检测，以及基于运行证据的搜索制度切换**。

### P2. ClaimCI：结论失效传播与选择性重验证

暂定题目：**ClaimCI: Active Claim Invalidation and Selective Re-execution for Scientific
Agents**。

#### 研究问题

当代码、数据、文献、模拟配置、传感器状态或环境条件发生变化时，系统能否自动判断哪些
科研结论已经失效，并只重跑恢复这些结论所需的最小工作流子图？

#### 核心定义

- [ ] 定义一等 `ScientificClaim`，包含适用范围、前提、证据依赖、验证器和有效状态；
- [ ] 支持 `UNVERIFIED`、`VALIDATED`、`STALE`、`CONTESTED`、`INVALIDATED`；
- [ ] 将数据版本、代码摘要、环境参数、文献证据和验证结果纳入 validity envelope；
- [ ] 上游证据撤销或条件漂移时沿依赖图传播失效；
- [ ] 计算最小受影响节点集合，并调用现有持久 DAG 进行选择性重跑；
- [ ] 只有新的独立验证通过，claim 才能重新进入 `VALIDATED`；
- [ ] 把 contradiction、regime shift 和跨分支复现作为正式验证器类型。

#### 最小实验

- MisKnow-Agent：在中间研究状态注入误导证据，测试错误结论采纳率及撤销传播；
- CAWM 风格任务：改变运行条件，测试“正确结果、错误机制”能否被标记；
- 科学模拟：注入代码、配置、数据和模拟器状态变化，比较全量重跑与选择性重跑。

主要指标：stale-claim false acceptance、错误传播深度、检测延迟、重跑规模、计算节省和有效
证据误拒率。

#### 创新边界

单纯记录 claim、artifact lineage 或 execution provenance 已经不足以构成贡献。ClaimCI 的
贡献是让 provenance 具有**运行时效力**：阻止失效结论继续参与计划，并触发最小重验证。

### P3. RecoverSpec：状态约束的恢复计划编译

暂定题目：**RecoverSpec: Compiling Diagnoses into Admissible Recovery Actions**。

#### 研究问题

系统能否把模型给出的 recovery intent 编译为对当前工作流、模拟器或物理环境真实可执行、
副作用可控且可验证的恢复计划？

- [ ] 为 `RecoveryAction` 增加 target、preconditions、资源约束、副作用、可逆性和
  postconditions；
- [ ] 从当前 DAG、artifact、process、resource 和 simulator state 生成 admissible action
  space；
- [ ] 在执行前完成 Schema 校验、目标绑定、权限检查和 dry-run/simulator check；
- [ ] 将不可逆动作拆分为 proposal、approval、commit；
- [ ] 执行后必须检查 postconditions 和独立验收，失败则保留为负经验而非可复用策略；
- [ ] 比较自由文本恢复、Schema 约束恢复和状态/模拟器约束恢复。

优先在可控科学软件和模拟器 fault injection 中验证，再扩展到具身任务的 affordance、碰撞、
安全边界和物理可行性检查。

## C. 后续候选，而非首篇主线

### C1. Epistemic Independence for Research Teams

- [ ] 区分组织并行与证据独立，测量分支之间的共享上下文和错误相关性；
- [ ] 支持 blind replication、proposer/verifier 隔离和独立随机种子；
- [ ] 研究怎样在固定预算下获得有效独立验证，而不是多个 Agent 重复同一种错误。

仅增加 reviewer、critic 或 scientist 角色不足以构成独立创新；必须定义和测量 epistemic
independence。

### C2. Human Attention Scheduler

- [ ] 基于错误代价、分支熵、不可逆性和信息价值决定何时询问人类；
- [ ] 合并低价值问题，避免用频繁确认掩盖系统缺乏自治；
- [ ] 以 verified progress per human intervention 作为核心指标。

该方向需要真实或高质量模拟的人类反馈评测，实验成本高于前三项。

## D. Core Enabling Capabilities and Non-Claims

以下内容都是 Nexgent 必须建设和测量的核心使能能力，但不单独作为主要研究贡献：

| 使能能力 | 在系统中的必要角色 | 不能采用的主张方式 |
| --- | --- | --- |
| `ResearchTeam` | P1 的条件化执行与组织层，P2/P3 的分支和责任载体 | “多 Agent 或增加角色即可提高科研表现” |
| Literature / Codebase Providers | 为 P2 提供版本化证据，为 P1/P3 提供文献与代码状态 | “接入搜索、总结、RAG 或代码问答” |
| Claim/Evidence 基础图 | P2 的类型化科学依赖数据平面 | “记录 provenance 本身保证结论正确” |
| Aligned checkpoint / safe retry | P1 分叉、P2 replay、P3 安全恢复的共同一致性协议 | “可以聊天回退、文件快照或普通重试” |
| Scoped invalidatable memory | 为 P1 提供历史信号，为 P2/P3 提供可撤销经验 | “加入长期记忆即可持续改进” |
| `ExperimentLedger + CandidatePolicy` | 防止 P1 被单分数贪心选择绑架 | “只保留最终分数最高的实验” |
| Capability ABI / dynamic shortlist | P1 `EXPAND` 与 P3 动作约束的能力面 | “向模型暴露更多插件或全部工具” |

对应的主要创新仍然是：**P1 的在线饱和检测与 research-regime switching、P2 的主动 claim
失效与最小重验证、P3 的 state-constrained recovery compilation。** 使能能力应作为系统实现、
可靠性保证、基线与消融变量报告。

## E. 推荐实施顺序

1. 完成 `Capability ABI + Event Log + aligned checkpoint`，先建立一致、可恢复的执行底座；
2. 建立类型化 Claim/Evidence/Artifact/Validator 基础图；
3. 实现 `ExperimentLedger + CandidatePolicy`，建立 champion、Pareto、多样性和负结果档案；
4. 将 `ResearchTeam` 与 scoped/provenance-backed memory 直接落入持久 Run/DAG；
5. 实现最小 LiteratureEvidenceProvider 与 CodebaseModelProvider；
6. 记录 research-progress、novelty、failure repetition、team diversity 和 capability-use telemetry，
   建立单智能体、静态多智能体和固定多样性搜索基线；
7. 实现 P1 的规则型 regime detector 与受预算控制的条件化分叉；
8. 在 P1 trace 上加入 ClaimCI 的主动失效、memory invalidation 和选择性 replay；
9. 将 capability action metadata、checkpoint safety 与 CodebaseModel 接入 RecoverSpec，先在科学
   软件和模拟器中验证，再扩展到具身智能。

三个最小闭环分别是：

- **P1**：ResearchTeam + checkpoint/fork + memory telemetry + ExperimentLedger + Capability ABI；
- **P2**：Claim/Evidence graph + Provider provenance + memory invalidation + selective replay；
- **P3**：CodebaseModel + action metadata + checkpoint safety + recovery compiler。

## F. 近邻工作与实验依据

- [Long-Horizon Autonomous Architecture Research with a Language-Model Agent](https://arxiv.org/abs/2608.01995)：观察搜索饱和、工作流诱导的贪心行为和 action-surface expansion 后恢复；
- [Towards Diverse Scientific Hypothesis Search with Large Language Models](https://arxiv.org/abs/2606.10587)：固定验证预算下的多温度多样性搜索；
- [ScienceFlow](https://arxiv.org/abs/2608.14354)：recoverable executable states、re-anchoring 和基于验证进展的资源分配；
- [Artifact-centered Claim-aware Observability](https://arxiv.org/abs/2608.18312)：claim-aware artifact lineage；
- [Is Deep Research Reliable?](https://arxiv.org/abs/2607.20891)：误导证据进入长周期研究后的错误结论传播；
- [Correct Answer, Wrong Mechanism](https://arxiv.org/abs/2606.23175)：机制不忠实及 regime-shift 检查；
- [R2Act](https://arxiv.org/abs/2607.04623)：诊断正确与恢复动作有效之间的显著差距；
- [AgentRewind](https://arxiv.org/abs/2608.14380)：Agent/环境对齐 checkpoint 与 rewind；
- [Verified Tool Calls](https://arxiv.org/abs/2608.02645)：timeout 后验证、幂等键与避免重复副作用；
- [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296)：不同任务结构下多智能体的收益、退化与条件化组织；
- [PaperQA2](https://arxiv.org/abs/2409.13740) 与 [OpenScholar](https://arxiv.org/abs/2411.14199)：可追踪文献检索与科学问答基线；
- [RepoGraph](https://arxiv.org/abs/2410.14684)：版本化代码图、局部结构上下文与代码任务增益；
- [Memory Management for LLM Agents](https://arxiv.org/abs/2505.16067)：选择性写入、删除和 naive memory growth 的退化；
- [How Many Tools Should an LLM Agent See?](https://arxiv.org/abs/2605.24660)：动态工具短列表的覆盖率、选择准确率与上下文收益；
- [FIRE-Bench](https://arxiv.org/abs/2602.02905)：完整科研洞见再发现评测；
- [SciAgentArena](https://arxiv.org/abs/2606.12736)：真实科研任务中的开放探索和稳健性缺口。

本文献列表用于界定 2026 年 8 月时点的近邻工作。开始论文写作前应重新检索并更新相关工作。
