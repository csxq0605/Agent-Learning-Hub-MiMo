![Nexgent — Agents in motion](nexgent/assets/brand/nexgent-title.png)

基于 [Agent Learning Hub](https://github.com/datawhalechina/Agent-Learning-Hub) 学习路线完成 Stage 0-8 实践，并在此基础上构建生产级、模型无关的 Agent Harness。Nexgent 现在同时提供原生 PyQt6 桌面 GUI、Textual TUI 与无界面 CLI，三种前端共用同一个 Agent、工具、权限、Session、SubAgent、Workflow 与扩展运行时。

## 阶段概览

| Stage | 主题 | 交付物 | 关键概念 |
|-------|------|--------|----------|
| 0 | 理论基础 | [学习笔记](stage-0/note-why-agent.md) | Agent vs Workflow、ReAct 范式 |
| 1 | 最小 Agent | [~220 行 Python agent](stage-1/) | Agent Loop、工具选择、安全数学求值 |
| 2 | RAG 研究助手 | [研究助手 agent](stage-2/) | 三级记忆、RAG 管线、引用 |
| 3 | Agent Harness | [Harness 演示](stage-3/) | 工具注册、权限门、会话存储 |
| 4 | 多 Agent 协作 | [多 agent 写作系统](stage-4/) | Supervisor 模式、角色分离、结构化 I/O |
| 5 | Skill 框架 | [Code Review Skill](stage-5/) | SKILL.md 格式、可复用工作流 |
| 6 | 浏览器自动化 | [浏览器研究 agent](stage-6/) | Playwright、安全守卫、审计追踪 |
| 7 | 评估框架 | [评估运行器](stage-7/) | 双层判定、失败分类、回归测试 |
| 8 | 生产级 DevOps Agent | [DevOps agent](stage-8/) | 可观测性、成本追踪、权限门 |

## Nexgent

基于 Stage 0-8 经验构建的生产级模型无关 Agent Harness，参考 Claude Code 架构，并采用 AutoReport/Manyselves 已验证的紧凑工作区交互方式。

**核心特性**：原生桌面 GUI、Agent Loop、38 个工具、MCP 工具桥接、6 种权限模式、安全管线、上下文管理、记忆系统、Session、Hook、SubAgent、Workflow、多模型配置、插件、Skills、TUI、CLI、自定义 Agent、后台任务、`@file` 引用与 Goal 管理。

详见 [Nexgent 产品文档](nexgent/README.md)、[桌面 GUI 说明](nexgent/docs/desktop-gui.md)和[真实可见验收记录](nexgent/docs/visible-gui-validation.md)。

## 原生桌面 GUI

![Nexgent desktop workspace](nexgent/assets/screenshots/main-window.png)

- Files、Sessions、Agents 共用紧凑左侧导航；中栏预览 Markdown、文本、代码和图片；右栏展示统一 Agent 对话与工具活动。
- `/` 命令与 `@` 文件支持动态候选和 Tab 补全；项目级输入历史支持 `↑`/`↓` 恢复草稿。
- 运行中可用 `/btw <指导>` 注入上下文，普通输入进入有界队列，Stop 同时停止主/子 Agent 并清除未执行输入。
- 写入、Plan 和动态问答使用 GUI 原生审批框；SubAgent 与 Workflow Agent 拥有独立可切换对话。
- 配置保存后立即重载模型；`/clear`、`/quit`、Session save/load/fork 和安全关闭均通过同一运行时完成。

真实 macOS 窗口验收覆盖 25 个功能场景并全部通过；远程模型完成了主 Agent 读取、可见审批、子 Agent `created → running → completed` 和结果回传。详见[完整验收证据](nexgent/docs/visible-gui-validation.md)。

## 快速开始

```bash
git clone https://github.com/csxq0605/Nexgent.git
cd Nexgent/nexgent
pip install -e .

# 配置密钥
cp .env.example .env
# 编辑 .env 填入 MIMO_API_KEY 等

# 配置模型（可选，有默认值）
cp models.json.example models.json

nexgent          # 原生桌面 GUI
nexgent --tui    # Textual TUI
nexgent --task "Review this project"  # 无界面 CLI
```

交互式运行 `nexgent` 默认启动原生桌面 GUI。管道输入、`--task`、`json` 与 `stream-json` 保持无 Qt 的自动化路径。

## 测试

| 类型 | 数量 |
|------|------|
| 单元测试 | 1057+ |
| E2E 测试 | 73（57 fast + 16 slow） |
| Stage 测试 | 67 |

2026-07-28 桌面交付复验：可见 GUI 25/25；代码套件 1017 passed、110 skipped；7 个因沙箱网络权限失败的 localhost/外网测试在授权环境重跑为 7/7 passed。

```bash
cd nexgent
pip install -e ".[dev]"
python -m pytest tests/ --ignore=tests/test_e2e.py -v  # 单元测试
python -m pytest tests/test_e2e.py -v                    # E2E fast
python -m pytest tests/test_e2e.py -v --run-slow         # E2E fast + slow
python run_tests.py --all                                 # 全部
```

## CI/CD

GitHub Actions 自动化测试：

- **unit-tests**: push/PR 自动运行，Python 3.10-3.13 矩阵，覆盖率报告上传 Codecov
- **e2e-fast**: 仅手动触发（`workflow_dispatch` 选择 `fast` 或 `all`）
- **e2e-full**: 仅手动触发（`workflow_dispatch` 选择 `all`）

## 项目结构

```
Nexgent/
├── stage-0/ ~ stage-8/    # 学习阶段交付物
├── nexgent/               # 生产级 Agent Harness（主要交付物）
│   ├── nexgent/           # Python 包
│   │   ├── agent.py       # 核心 Agent Loop
│   │   ├── cli.py         # REPL + 斜杠命令
│   │   ├── gui/           # PyQt6 原生桌面工作区
│   │   ├── runtime/       # GUI/TUI/CLI 共用运行时与事件
│   │   ├── workflow.py    # 工作流引擎
│   │   ├── models.py      # 多模型配置
│   │   ├── plugins.py     # 插件系统
│   │   ├── mcp.py         # MCP 集成（工具桥接）
│   │   ├── tui.py         # 全屏 TUI 界面
│   │   ├── tools/         # 14 个工具模块（38 个工具）
│   │   ├── resources/     # 打包应用图标
│   │   └── ...
│   ├── assets/            # Agent Relay 品牌与 GUI 截图
│   ├── docs/              # GUI、品牌与验收文档
│   ├── tests/             # 单元 + E2E 测试
│   ├── models.json.example  # 模型配置模板
│   └── setup.py
├── tests/                 # Stage 级别测试
└── .github/workflows/     # CI/CD
```

## License

MIT License
