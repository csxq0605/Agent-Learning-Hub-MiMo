# Nexgent Desktop GUI

`nexgent` 在交互式终端中默认启动 PyQt6 桌面应用；`nexgent --tui` 保留 Textual 界面；`--task`、管道输入、`json` 和 `stream-json` 始终保持无 Qt 的 CLI 路径。

## 功能映射

| GUI 区域 | 使用的 Nexgent 能力 |
| --- | --- |
| Files | 项目文件浏览、`@file` 候选来源、文本/代码/Markdown/图片预览 |
| Sessions | JSONL 自动保存、恢复、分叉、保存与加载 |
| Agents | 主 Agent 与每个 SubAgent 的生命周期、任务和独立对话结果 |
| Conversation | 主 Agent 运行、模型/权限切换、工具活动、停止、写入确认 |
| Composer | `/` 命令与 `@` 文件动态候选、Tab 补全、项目级输入历史、运行中指导与排队 |

GUI 不再为每个命令维护按钮矩阵。`nexgent.commands.SLASH_COMMANDS` 是 `/` 候选的唯一来源，`scan_completions()` 同时服务 GUI 与终端的 `@` 文件候选。命令继续由 `CommandService` 调用原有 `_handle_command`；普通消息、`@` 引用和 `!` Shell 继续由 `NexgentRuntime` 路由到同一个 `NexgentAgent` 与 `PermissionGate`。

运行期间 Composer 保持可输入。`/btw` 通过线程安全 Session 注入当前上下文，普通输入进入有界 FIFO 队列。SubAgent 创建、运行、完成、失败和取消都会发出 `SUBAGENT_CHANGED`，GUI据此创建可切换的 Agent 记录；隔离子会话保存在 `.nexgent/sessions/agents/`。

## 安全与线程

耗时运行发生在 Qt 主线程之外。`RuntimeBridge` 只通过 Qt signal 把事件送回窗口。写入和执行确认通过 `InteractionBroker` 传给主线程的模态确认框；没有 handler、超时、窗口关闭或 handler 异常都返回拒绝。Stop 会同时请求主 Harness 中止并调用 `SubAgentManager.cancel_all()`；活动子 Harness 会收到自己的 graceful-abort 请求。

## 开发与验证

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
QT_QPA_PLATFORM=offscreen .venv/bin/pytest -q tests/gui
QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/capture_gui_screenshots.py
```

品牌位图使用 `scripts/build_brand_assets.py` 从 `assets/brand/*.svg` 生成。发布前应再次运行构建脚本并确认生成哈希没有变化。
