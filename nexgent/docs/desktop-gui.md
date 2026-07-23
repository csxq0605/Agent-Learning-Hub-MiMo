# Nexgent Desktop GUI

`nexgent` 在交互式终端中默认启动 PyQt6 桌面应用；`nexgent --tui` 保留 Textual 界面；`--task`、管道输入、`json` 和 `stream-json` 始终保持无 Qt 的 CLI 路径。

## 功能映射

| GUI 区域 | 使用的 Nexgent 能力 |
| --- | --- |
| Workspace | 项目文件浏览、`@file` 引用来源、文本/代码/Markdown/图片预览 |
| Sessions | JSONL 自动保存、恢复、分叉、保存与加载 |
| Agent | 主 Agent 运行、流式输出、模型切换、六种权限模式、停止、写入确认 |
| Run | Background Tasks、单个/并行/Pipeline SubAgents |
| Automate | Workflow 运行/恢复/保存、Goal 设置/状态/清理 |
| Extensions | MCP、Plugins、Skills、Custom Agents、Hooks |
| State | Checkpoint rewind、Memory、Context、Compact、Stats、Tools、Project init |

所有控制中心动作都发送到 `CommandService`，后者调用原有 `_handle_command`。普通消息、`@` 引用和 `!` Shell 由 `NexgentRuntime` 路由到同一个 `NexgentAgent` 与 `PermissionGate`。因此增加 GUI 不会产生第二套 Agent loop、权限规则或扩展状态。

## 安全与线程

耗时运行发生在 Qt 主线程之外。`RuntimeBridge` 只通过 Qt signal 把事件送回窗口。写入和执行确认通过 `InteractionBroker` 传给主线程的模态确认框；没有 handler、超时、窗口关闭或 handler 异常都返回拒绝。

## 开发与验证

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
QT_QPA_PLATFORM=offscreen .venv/bin/pytest -q tests/gui
QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/capture_gui_screenshots.py
```

品牌位图使用 `scripts/build_brand_assets.py` 从 `assets/brand/*.svg` 生成。发布前应再次运行构建脚本并确认生成哈希没有变化。
