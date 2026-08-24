# ADR-0002：CapabilityDescriptor 是权威契约，ToolDef 只是 Adapter

- 状态：Accepted
- 日期：2026-08-24
- 关联：`CON-004`、`CAP-001..006`、`INV-005..006`

## 背景

当前 `ToolDef` 直接服务模型 tool schema，只有 name、description、parameters、handler 与
少量权限/安全标记。同名注册会覆盖，built-in、plugin 和 MCP 也没有统一版本、错误、输出、
effect、health 和重放语义。

把更多字段直接堆入 `ToolDef` 会继续混淆“模型看见的函数”和“运行时可治理的能力”。

## 决策

新增 provider-neutral、可持久化的 `CapabilityDescriptor` 和 `CapabilityBinding`，前者是
权威 ABI，后者记录一次 Run 实际解析的 provider/version/digest。

`ToolDef` 保留为 handler 与 OpenAI-compatible schema Adapter，并显式引用一个 descriptor。
built-in、plugin、MCP 和未来 simulator/robot capability 都必须先通过同一 conformance suite，
再生成对应 Adapter。

Registry 默认拒绝冲突；Resolver 只向节点暴露 shortlist，历史 Run 使用 binding manifest
重放。

## 后果

- 需要保持旧 `ToolDef(...)` 构造兼容，并为内置工具生成默认 descriptor；
- plugin / MCP bridge 必须补 provider、version、effect 和 health；
- install/load/unload 要原子替换 registry snapshot；
- 初期 descriptor 元数据可能是 conservative/unknown；unknown effect 必须 fail closed，不能
  猜成 read-only 或 idempotent。
