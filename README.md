![Nexgent — Agents in motion](nexgent/assets/brand/nexgent-title.png)

Nexgent 是面向长周期科研代码与模拟任务的可追踪、自排查、自进化 Coding Harness。
它让 Agent 在真实仓库中修改代码、配置和模拟参数，同时把执行、故障、恢复与验收证据
保存为可继续、可检查、可导出的持久 Run。

> A traceable, self-diagnosing and evolving Coding Harness for long-running
> research code and simulation tasks.

## 功能

- **验证驱动闭环**：以用户提供的测试或模拟验收命令作为唯一成功条件；普通模型回答
  不会被当作任务完成。
- **持久追踪**：记录目标、attempt、模型和工具事件、进程、代码/配置变化、产物、
  依赖边、诊断、恢复和验证结果。
- **自动排查**：验收失败后，从症状沿控制、数据、产物、资源和因果关系回溯候选根因，
  将证据与失败输出交给下一次修复。
- **长周期恢复**：Run 保存在项目的 `.nexgent/runs`；暂停或中断后可由新进程继续同一
  Run，并使用 lease 防止两个运行时同时接管。
- **验证约束的经验演化**：成功恢复只有经过独立验收且没有回归才会晋升为可复用策略；
  复用后失败会降权并可被禁用。
- **科研运行时**：提供 Typed DAG、精确输入缓存、跨进程恢复、模拟器状态、资源状态和
  外部副作用遥测接口。
- **统一工作区**：PyQt6 GUI、Textual TUI 与无界面 CLI 共用同一个 Agent、权限系统、
  Session、SubAgent、Workflow 和持久 Harness。

![Nexgent desktop workspace](nexgent/assets/screenshots/main-window.png)

## 安装

要求 Python 3.10+。

```bash
git clone https://github.com/csxq0605/Nexgent.git
cd Nexgent/nexgent

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
cp models.json.example models.json
```

在 `.env` 中填写所使用 Provider 的 API Key，并在 `models.json` 中选择默认模型。

## 启动

```bash
# 原生桌面 GUI
nexgent-gui --project /path/to/repository

# 默认交互入口；也可显式使用 TUI
nexgent
nexgent --tui

# 单次无界面任务
nexgent --task "Inspect the repository and explain the failing simulation"
```

## 运行科研 Coding Loop

在 GUI、TUI 或交互终端中执行：

```text
/harness run \
  --check "python simulate.py --verify" \
  --task "Find and repair the numerical instability" \
  --attempts 3 \
  --timeout 120
```

Nexgent 会重复执行 Agent、独立验收、故障记录、依赖定位和恢复指导。只有验收命令退出码
为 0，Run 才会进入 `succeeded`；预算耗尽时保持 `paused`，不会伪报成功。

## 管理长周期 Run

```text
/harness list
/harness status <run-id>
/harness resume <run-id> --attempts 3 --timeout 120
/harness export <run-id>
```

默认导出到 `.nexgent/exports/<run-id>.jsonl`。可在另一个环境中独立检查：

```bash
nexgent-verify-run \
  --jsonl .nexgent/exports/<run-id>.jsonl \
  --strict-lifecycles
```

## 当前能力边界

- Nexgent 提供 Harness、追踪协议和恢复闭环；项目效果评估由外部任务体系负责。
- “自进化”指经过验证的恢复经验晋升、复用、降权和禁用，不表示在线训练基础模型，也不
  会绕过权限自动重放任意补丁。
- 通用代码与进程事件会自动记录；领域模拟器内部状态需要通过 `SimulatorAdapter` 接入。
- 任意未知科研仓库能否修复取决于模型、工具、遥测、验收条件和权限配置。

## 测试

```bash
cd Nexgent/nexgent
pip install -e ".[dev]"
QT_QPA_PLATFORM=offscreen pytest -q
```

完整使用说明见 [Harness README](nexgent/README.md)，桌面操作见
[Desktop GUI](nexgent/docs/desktop-gui.md)。

## License

[MIT](LICENSE)
