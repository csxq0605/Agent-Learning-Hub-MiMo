# 科研智能体路线图（2026-08）

> 状态：规划中。本页描述待研究、待验证和待实现的方向，不代表当前版本已经提供这些能力。

Nexgent 当前定位是面向长周期科研代码与模拟任务的持久、可追踪、验证驱动 Coding
Harness。下一阶段分成两条相互配合但必须明确区分的路线：

1. **能力内化**：把多智能体组织、文献研究和代码库建模变成 Harness 的一等能力；
2. **研究创新**：围绕科研过程的搜索饱和、结论失效和恢复动作可执行性，提出新的运行时
   定义、控制机制和可复现实验。

多智能体、文献检索或代码扫描本身不作为主要研究贡献。它们是实施科研过程控制的能力
底座。

## A. 能力内化

### A1. ResearchTeam：一等多智能体组织

目标是把 lead / manager / worker 的层级组织直接内化到持久 `ResearchRun`，而不是维护
一套与 Run、Workflow 和证据链分离的任务系统。

- [ ] 定义 `ResearchTeam`、成员角色、父子关系、能力集合与资源预算；
- [ ] 让 Team Lead 对完整 `ResearchRun` 负责；
- [ ] 让 Manager 管理子 DAG、研究分支及其局部预算；
- [ ] 让 Worker 执行具体 `WorkflowNode`，并把输出记录为 `ArtifactRecord`；
- [ ] 将 team task 和 dependency 映射到现有 Typed DAG；
- [ ] 将消息、委派、交接和决策记录为有序 Run Event；
- [ ] 保留 subordinate request、inbox 和两阶段 shutdown，避免提前关闭仍有依赖的成员；
- [ ] 支持不同分支使用不同模型、上下文、工具和文献视野，为认知多样性提供机制基础；
- [ ] 所有 Agent 写入、Shell、作业提交和外部副作用继续经过统一权限与审计管线。

验收条件：中断进程后，新运行时可以恢复同一个团队、任务依赖、成员状态、预算和证据链；
任何团队产出都可以追溯到对应 Run、WorkflowNode、输入证据和执行者。

### A2. LiteratureEvidenceProvider：持久文献证据层

文献能力不应停留在“搜索并总结论文”，而应向假设生成、反证和结论验证提供结构化、可
撤销的科研证据。

- [ ] 定义 `PaperArtifact`、`LiteratureClaim`、`CitationEdge` 和 `QuerySnapshot`；
- [ ] 持久保存检索式、来源、获取时间、版本、过滤过程和全文/元数据摘要；
- [ ] 区分 primary evidence、secondary synthesis 和 agent-generated interpretation；
- [ ] 同一文献证据同时可供 hypothesis、reviewer 和 falsification Agent 使用；
- [ ] 记录文献版本更新、撤稿、相互矛盾和来源可信状态；
- [ ] 将文献 claim 接入依赖图，使证据撤销可以影响下游计划和结论；
- [ ] 默认使用有效 TLS、版本固定和可重放查询，避免以不安全或不可复现的请求作为证据。

### A3. CodebaseModelProvider：代码库结构模型

代码库能力的目标不是提供另一个仓库问答工具，而是把代码结构变成实验、诊断和结论依赖
中的正式对象。

- [ ] 索引模块、符号、入口、配置、测试、构建目标和版本提交；
- [ ] 将代码符号、修改、测试和运行产物连接到 `ArtifactRecord` 与 `DependencyEdge`；
- [ ] 支持变更影响分析、失败定位和最小受影响子图重跑；
- [ ] 为科研 Agent 提供受预算约束的结构化上下文，而非一次性全文扫描；
- [ ] 在 fresh process 中重建或加载同一版本的代码结构快照。

### A4. Capability ABI

在接入或内化外部能力前，先建立统一的能力契约。

- [ ] 统一工具定义、输入输出 Schema、错误语义、权限、版本和健康检查；
- [ ] 为 capability、plugin、agent profile 和安装目标提供稳定命名空间；
- [ ] 禁止不同来源因相同仓库尾名或短名称覆盖彼此；
- [ ] 能力必须通过最小可执行验证后才能进入可调度注册表；
- [ ] 支持按需发现和激活能力，避免把全部工具说明长期塞入 Agent 上下文。

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

## D. 暂不作为独立创新声明

以下能力可以建设，但不应单独宣传为研究创新：

- 通用多智能体协作或角色分工；
- 普通文献搜索、总结和代码库问答；
- 仅记录 claim/evidence graph；
- 通用 checkpoint、rollback 或 retry；
- 普通长短期记忆；
- 只根据最终分数保留最佳实验；
- 仅把更多插件或工具暴露给模型。

## E. 推荐实施顺序

1. 完成 Capability ABI，并让 ResearchTeam 任务直接落入持久 Run/DAG；
2. 实现最小 LiteratureEvidenceProvider 与 CodebaseModelProvider；
3. 记录 research-progress、novelty、failure repetition 和 capability-use telemetry；
4. 建立静态单智能体、静态多智能体和固定多样性搜索基线；
5. 实现 P1 的规则型 regime detector 与受预算控制的分叉；
6. 在 P1 稳定后加入 ClaimCI，作为跨分支结论与机制验证层；
7. 将 RecoverSpec 接入模拟器，形成面向具身智能的状态约束恢复接口。

## F. 近邻工作与实验依据

- [Long-Horizon Autonomous Architecture Research with a Language-Model Agent](https://arxiv.org/abs/2608.01995)：观察搜索饱和、工作流诱导的贪心行为和 action-surface expansion 后恢复；
- [Towards Diverse Scientific Hypothesis Search with Large Language Models](https://arxiv.org/abs/2606.10587)：固定验证预算下的多温度多样性搜索；
- [ScienceFlow](https://arxiv.org/abs/2608.14354)：recoverable executable states、re-anchoring 和基于验证进展的资源分配；
- [Artifact-centered Claim-aware Observability](https://arxiv.org/abs/2608.18312)：claim-aware artifact lineage；
- [Is Deep Research Reliable?](https://arxiv.org/abs/2607.20891)：误导证据进入长周期研究后的错误结论传播；
- [Correct Answer, Wrong Mechanism](https://arxiv.org/abs/2606.23175)：机制不忠实及 regime-shift 检查；
- [R2Act](https://arxiv.org/abs/2607.04623)：诊断正确与恢复动作有效之间的显著差距；
- [AgentRewind](https://arxiv.org/abs/2608.14380)：Agent/环境对齐 checkpoint 与 rewind；
- [FIRE-Bench](https://arxiv.org/abs/2602.02905)：完整科研洞见再发现评测；
- [SciAgentArena](https://arxiv.org/abs/2606.12736)：真实科研任务中的开放探索和稳健性缺口。

本文献列表用于界定 2026 年 8 月时点的近邻工作。开始论文写作前应重新检索并更新相关工作。
