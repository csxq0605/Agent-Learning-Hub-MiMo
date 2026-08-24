# 科研运行时交付进度与设计偏差

> 最近审计：2026-08-24
> 审计基线：branch `roadmap/research-agent-next`, commit `77eddf9`
> 规范来源：[specs/research-runtime-spec.md](specs/research-runtime-spec.md)

本页是持续更新的实现证据台账。它不复述愿景，只回答三个问题：

1. 规范要求当前是否真正成立；
2. 哪些代码、测试或实验能够证明；
3. 设计与实际的差距是什么，下一步如何消除。

## 1. 状态规则

只允许四种状态：

- `UNIMPLEMENTED`：没有能满足语义的实现；
- `PARTIAL`：存在字段、局部路径或测试，但不足以证明完整 requirement；
- `CONFORMANT`：代码、自动化验证和所需故障/实验输出共同证明 requirement；
- `WAIVED_BY_ADR`：通过 ADR 明确改变或豁免规范，并记录迁移与影响。

更新规则：

- 代码存在但未进入真实执行路径，仍为 `PARTIAL`；
- 单元测试不能替代跨进程、故障注入或 benchmark 要求；
- 证据路径必须指向稳定 symbol、test name、导出 artifact 或报告；
- 每次实现提交同时更新“实际状态”“剩余差距”和“本次纠偏”；
- README 只能宣称 `CONFORMANT` 能力，计划和局部骨架留在本页。

## 2. 里程碑

| Milestone | 目标 | 当前 | 完成门 |
| --- | --- | --- | --- |
| M0 | Specification Lock | `PARTIAL` | 最终定位、层级、契约、不变量、评价协议、初始偏差和 ADR 全部入库 |
| M1 | Runtime Kernel | `PARTIAL` | Capability ABI、aligned checkpoint、effect ledger、schema migration、strict export |
| M2 | Enabling Research Plane | `UNIMPLEMENTED` | ResearchTeam、ExperimentLedger、Claim/Evidence、MemoryView、两个 Provider |
| M3 | P1 Regime Controller | `UNIMPLEMENTED` | telemetry、规则/统计 detector、regime machine、基线与消融 |
| M4 | P2 ClaimCI | `UNIMPLEMENTED` | validity gate、失效传播、memory withdrawal、minimal revalidation |
| M5 | P3 RecoverSpec | `PARTIAL` | intent、admissible space、checked plan、effect commit、postconditions |
| M6 | Integrated Reference Run | `UNIMPLEMENTED` | 一个同时覆盖 regime、invalidation、recovery、kill/resume 的公开运行包 |

### 当前测试基线

- 核心 Runtime / Registry / GoalController / golden trace：`93 passed in 19.21s`；
- 命令范围：`test_registry.py`、`test_goal_controller.py`、`test_golden_research_trace.py` 和全部
  `test_runtime_*.py`；
- 系统 Python 缺少 OpenAI SDK 与 PyQt6；基线使用仅供导入的临时 OpenAI stub，运行后已删除；
- GUI 与完整 suite 尚未形成 baseline，不能据此声称 M0 的“全量测试 baseline”已经完成。

## 3. 不变量审计

| Requirement | 状态 | 当前证据 | 尚缺的证明 |
| --- | --- | --- | --- |
| `INV-001` 单一事实源 | `PARTIAL` | `SQLiteRunStore`、content-addressed artifact、JSONL export | 科研 MemoryView/索引删除后的完整重建 |
| `INV-002` provenance closure | `PARTIAL` | Event、Artifact、DependencyEdge、strict lifecycle verifier | claim、experiment、team、effect 的 closure |
| `INV-003` verified success | `PARTIAL` | `GoalController`、`VerificationResult`、coding-loop tests | schema 2.0 Research/Experiment 全层级 property test |
| `INV-004` epistemic admission | `UNIMPLEMENTED` | 无一等 ScientificClaim | claim state × purpose gate 与 mutation suite |
| `INV-005` capability fail-closed | `PARTIAL` | unknown tool/permission/input fail closed | 同名冲突、版本、health、conformance |
| `INV-006` dynamic shortlist | `UNIMPLEMENTED` | Agent 当前调用 `registry.list_tools()` 全量暴露 | Resolver、选择理由、context telemetry |
| `INV-007` verify-before-retry | `UNIMPLEMENTED` | 仅有普通 retry 与 idempotency 字段 | effect unknown 状态与 postcondition gate |
| `INV-008` irreversible lifecycle | `PARTIAL` | `HarnessTelemetry.record_side_effect` 要求 approval | proposal/dispatch/commit/postcondition 状态机 |
| `INV-009` aligned resume | `PARTIAL` | file checkpoint、Run resume、DAG result resume | Agent/DAG/environment/effect 一致切面与 crash matrix |
| `INV-010` negative retention | `PARTIAL` | 失败 Run、diagnosis、verification 持久化 | ExperimentLedger 与 non-destructive CandidatePolicy |
| `INV-011` durable team | `UNIMPLEMENTED` | SubAgent 事件可进入 active Run | team/task/handoff/budget 一等实体和 fresh resume |
| `INV-012` hierarchical hard budget | `PARTIAL` | Run/Goal/SubAgent 有部分时长、步骤和 token 字段 | 执行期 token/cost、父子预算和并发硬停止 |
| `INV-013` version closure | `PARTIAL` | run 记录 code/environment/model/prompt/tool digest | 数据、capability binding、validator 与评价版本完整 gate |
| `INV-014` admissible recovery | `PARTIAL` | RecoveryAction 有 target/risk/approval/idempotency | pre/postconditions、resource、dry-run、真实 state binding |
| `INV-015` frontend neutrality | `PARTIAL` | GUI/TUI/CLI 共享 `NexgentRuntime` | 新的 P1/P2/P3 服务必须保持同一路径，补 parity trace |
| `INV-016` control precedence | `UNIMPLEMENTED` | 权限 gate 局部优先 | safety > validity > search 的显式冲突测试 |

## 4. 使能能力审计

| Requirement group | 状态 | 下一可验收纵切 |
| --- | --- | --- |
| `CAP-001..006` | `PARTIAL` | 权威 CapabilityDescriptor + 冲突拒绝 + built-in conformance + resolver 接入 |
| `REC-001..006` | `PARTIAL` | EffectRecord 生命周期 + verify-before-retry，随后 aligned checkpoint |
| `CLM-001..005` | `UNIMPLEMENTED` | ScientificClaim/Evidence/ClaimEdge schema 与 store round-trip |
| `EXP-001..005` | `UNIMPLEMENTED` | EvaluationProtocol + ExperimentRecord + non-destructive ledger views |
| `TEAM-001..005` | `PARTIAL` | ResearchTeam/Member/Task 映射到单写者 RunStore |
| `MEM-001..005` | `PARTIAL` | provenance-backed MemoryViewItem 与 evidence-revocation retrieval gate |
| `PROV-001..005` | `UNIMPLEMENTED` | Provider protocol、versioned snapshot 和最小 fake-provider conformance |

## 5. 设计—实现偏差

| ID | Requirement | 当前实现 | 实际偏差 | 影响 | 解决里程碑 |
| --- | --- | --- | --- | --- | --- |
| `DIV-001` | `CON-001..002` | schema 1.0 `ExperimentRun` 同时承担顶层 Run 和分支语义 | `SEMANTIC` | P1 branch、评价与预算边界混淆 | M1 |
| `DIV-002` | P1 | `GoalController` 只有单目标执行闭环 | `MISSING` | 无外层 research regime | M3 |
| `DIV-003` | `CON-007` | `DependencyEdge` 表示执行关系，端点是字符串 | `MISSING` | 无科学 claim validity | M2 |
| `DIV-004` | `CON-012` | `RecoveryAction` 有 target/risk/approval/idempotency | `PARTIAL` | 缺 pre/postcondition、资源与 admissibility | M5 |
| `DIV-005` | `CON-010` | `CheckpointManager` 主要是文件快照 | `SEMANTIC` | 无 aligned research checkpoint | M1 |
| `DIV-006` | `CON-004` | `ToolRegistry.register` 同名覆盖；`ToolDef` 无版本/health/effect/cost | `SAFETY` | 不可重放、冲突和上下文膨胀 | M1 |
| `DIV-007` | `CON-009` | `MemoryStore` 是 Markdown 主题条目 | `SEMANTIC` | 无 provenance、scope、validity、撤销 | M2 |
| `DIV-008` | `CON-005/008/013` | team/regime/claim 只能进入自由 payload | `EVIDENCE` | 生命周期无法 strict verify | M1–M3 |
| `DIV-009` | `CON-008` | Run-level SQLite lease；SubAgent 状态在进程内 | `PERSISTENCE` | fresh-process 无法恢复团队 | M2 |
| `DIV-010` | `INV-009` | workspace pre/postimage 仅覆盖部分工具/文件 | `PARTIAL` | 不能证明完整 effect/checkpoint 边界 | M1 |
| `DIV-011` | `CON-009` | RecoveryStrategy 只从 accepted verification 晋升 | `PARTIAL` | 窄域经验尚未统一到 claim-aware memory | M2 |
| `DIV-012` | `INV-015` | 三前端共享 Runtime，是正确基础 | `PARTIAL` | 后续策略若进入 UI 会产生语义分叉 | 全程 |
| `DIV-013` | `INV-012` | SubAgent `max_tokens` 主要表示上下文窗口 | `SEMANTIC` | 不能证明执行期累计 token/cost 硬预算 | M2 |

偏差关闭必须同时满足：

1. 目标契约进入权威模块；
2. 真实执行路径消费它；
3. 持久化、导出和 fresh-process 恢复覆盖它；
4. 与 requirement 范围匹配的自动化证据通过；
5. 本表改为 `resolved` 并链接 commit / test / report。

## 6. 当前执行计划

1. **M0 收敛**：完成评价协议、术语、schema 2.0 迁移 ADR，并建立自动进度校验；
2. **M1-A Capability**：新增权威 ABI，不原地把 `ToolDef` 伪装成完整 capability；完成冲突拒绝、
   descriptor digest、binding manifest 和 built-in conformance；
3. **M1-B Effect**：引入 `EffectRecord` 生命周期、postcondition verifier 与
   verify-before-retry；
4. **M1-C Checkpoint**：定义 aligned snapshot manifest，先覆盖 Run/DAG/artifact/workspace/effect，
   再扩展 simulator/process；
5. **M2 Evidence**：增加 Claim/Evidence 和 ExperimentLedger，随后接 MemoryView 与 Team；
6. **M3–M5**：每个研究控制面先建立规则/确定性版本和反证测试，再运行 benchmark；
7. **M6**：选择公开科学模拟项目完成 integrated reference run 与独立导出验证。

## 7. 本轮纠偏记录

### 2026-08-24 / baseline

- 将“最终系统是什么”从混合路线图中拆出为规范；
- 明确 `ResearchRun → Branch → Experiment → Attempt → Node`，不再长期复用旧
  `ExperimentRun` 表达所有层级；
- 明确 P1/P2/P3 分别是 search、epistemic、action control，且共享单一事实源；
- 将多智能体、文献/代码 Provider、记忆、checkpoint、实验档案和工具路由列为使能层；
- 依据 ScienceFlow 收紧“可恢复研究状态”的新颖性；
- 依据 non-atomic failure 与 semantic rollback 研究，把 effect ledger、postcondition 和
  replay-or-fork 写成 checkpoint 的必要语义；
- 发现当前代码与最终定义的 13 项初始偏差，后续按本表逐项关闭。
