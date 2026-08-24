# ADR-0001：科研运行层级与三个控制面

- 状态：Accepted
- 日期：2026-08-24
- 关联：`CON-001..003`、`INV-016`

## 背景

schema 1.0 的 `ExperimentRun` 同时承担顶层任务、研究分支和一次执行的语义。现有
`GoalController` 适合单目标修复闭环，但无法清晰表达跨分支科研控制、claim validity 和
受状态约束的恢复。

## 决策

schema 2.0 使用：

`ResearchRun → ResearchBranch → ExperimentRun → RunAttempt → WorkflowNode`。

P1 Regime Controller 位于 Experiment/Branch 外层；P2 ClaimValidityService 是持续准入门和
revalidation planner；P3 RecoveryCompiler 位于单任务恢复内层，只产生 checked plan。

控制优先级为：

`Human authority and safety > claim validity > search optimization`。

所有控制面共享 `SQLiteRunStore + ArtifactStore`，不得各自维护事实数据库。

## 兼容性

旧 `ExperimentRun` 保持 schema 1.0 语义。显式 migrator 将它导入一个
`ResearchRun + default ResearchBranch + ExperimentRun`，不原地重解释历史字段。
`parent_run_id` 与 `branch_from_event_id` 的旧值进入迁移后的 branch lineage。

## 后果

- 需要 schema 2.0 契约、迁移器和双版本读取测试；
- P1 不会污染现有 GoalController 状态机；
- P2 无权直接调度，P3 无权直接执行；
- 导出 verifier 必须验证跨层引用和控制优先级。
