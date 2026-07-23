"""AutoReport-style three-column Nexgent workspace."""

from __future__ import annotations

import os
import re
from pathlib import Path

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QMainWindow, QMessageBox,
    QPushButton, QSplitter, QStatusBar, QVBoxLayout, QWidget, QInputDialog,
)

from ..context import CheckpointManager, Session
from ..branding import PRODUCT_NAME, TAGLINE
from ..models import get_model_registry
from ..runtime.events import RuntimeEventKind
from .config_dialog import ConfigDialog
from .icons import load_app_icon
from .runtime_bridge import RuntimeBridge
from .theme import theme_stylesheet
from .widgets.agent_panel import AgentPanel
from .widgets.control_center import ControlCenter
from .widgets.file_tree import ProjectFileTree
from .widgets.preview import PreviewPane

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class MainWindow(QMainWindow):
    def __init__(self, runtime, parent=None):
        super().__init__(parent)
        self.runtime = runtime
        self.project_root = runtime.project_root
        self.bridge = RuntimeBridge(runtime, self)
        self.settings = QSettings("Nexgent", "Desktop")
        self.setWindowTitle(f"{PRODUCT_NAME} — {self.project_root.name}")
        self.setWindowIcon(load_app_icon())
        self.setMinimumSize(1100, 720)
        self.resize(1480, 900)
        self.setStyleSheet(theme_stylesheet())
        self._build_menu()
        self._build_ui()
        self._connect_runtime()
        self._refresh_sessions()
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("File")
        config = QAction("Model & Provider Settings…", self)
        config.triggered.connect(self._open_config)
        file_menu.addAction(config)
        file_menu.addSeparator()
        quit_action = QAction("Close", self)
        quit_action.setShortcut("Ctrl+W")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        view = self.menuBar().addMenu("View")
        toggle = QAction("Toggle Control Center", self)
        toggle.setShortcut("Ctrl+J")
        toggle.triggered.connect(lambda: self.control.setVisible(not self.control.isVisible()))
        view.addAction(toggle)
        help_menu = self.menuBar().addMenu("Help")
        command_help = QAction("Nexgent Commands", self)
        command_help.triggered.connect(lambda: self.bridge.submit("/help"))
        help_menu.addAction(command_help)

    def _panel_header(self, title, subtitle=""):
        host = QWidget()
        row = QHBoxLayout(host)
        row.setContentsMargins(8, 6, 8, 6)
        label = QLabel(title)
        label.setObjectName("Section")
        row.addWidget(label)
        if subtitle:
            detail = QLabel(subtitle)
            detail.setObjectName("Muted")
            row.addWidget(detail)
        row.addStretch()
        return host

    def _build_ui(self):
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(8, 8, 8, 8)
        top = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(load_app_icon().pixmap(24, 24))
        brand = QLabel(PRODUCT_NAME.upper())
        brand.setObjectName("Brand")
        tagline = QLabel(TAGLINE)
        tagline.setObjectName("Muted")
        workspace = QLabel(f"Workspace · {self.project_root.name}")
        workspace.setObjectName("Muted")
        top.addWidget(logo)
        top.addWidget(brand)
        top.addWidget(tagline)
        top.addStretch()
        top.addWidget(workspace)
        outer.addLayout(top)

        vertical = QSplitter(Qt.Orientation.Vertical)
        columns = QSplitter(Qt.Orientation.Horizontal)

        left = QFrame()
        left.setObjectName("Panel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.addWidget(self._panel_header("WORKSPACE", self.project_root.name))
        self.file_tree = ProjectFileTree(self.project_root)
        left_layout.addWidget(self.file_tree, 3)
        left_layout.addWidget(self._panel_header("SESSIONS"))
        self.sessions = QListWidget()
        self.sessions.setToolTip("Double-click a session to resume it")
        left_layout.addWidget(self.sessions, 1)

        center = QFrame()
        center.setObjectName("Panel")
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(6, 6, 6, 6)
        center_layout.addWidget(self._panel_header("PREVIEW", "Markdown · code · images"))
        self.preview = PreviewPane()
        center_layout.addWidget(self.preview, 1)

        self.agent = AgentPanel(self.runtime.harness.model)
        registry = get_model_registry()
        registry.load()
        for profile in registry.list_profiles():
            if profile.model_name != self.runtime.harness.model:
                self.agent.model.addItem(profile.full_id)

        columns.addWidget(left)
        columns.addWidget(center)
        columns.addWidget(self.agent)
        columns.setSizes([280, 540, 600])
        columns.setStretchFactor(1, 2)
        columns.setStretchFactor(2, 2)
        vertical.addWidget(columns)

        self.control = ControlCenter()
        vertical.addWidget(self.control)
        vertical.setSizes([650, 210])
        outer.addWidget(vertical, 1)
        self.setCentralWidget(root)
        status = QStatusBar()
        self.status_model = QLabel(self.runtime.harness.model)
        self.status_session = QLabel(f"Session {self.runtime.session.session_id}")
        status.addWidget(self.status_session)
        status.addPermanentWidget(self.status_model)
        self.setStatusBar(status)

        self.file_tree.file_selected.connect(self.preview.open_file)
        self.sessions.itemDoubleClicked.connect(self._resume_session)
        self.agent.submitted.connect(self._submit)
        self.agent.stop_requested.connect(self.bridge.abort)
        self.agent.mode_changed.connect(self._change_mode)
        self.agent.model.currentTextChanged.connect(self._change_model)
        self.control.command_requested.connect(self._capability_command)

    def _connect_runtime(self):
        self.bridge.run_started.connect(self._run_started)
        self.bridge.run_finished.connect(self._run_finished)
        self.bridge.run_failed.connect(self._run_failed)
        self.bridge.busy_changed.connect(self.agent.set_busy)
        self.bridge.event_received.connect(self._runtime_event)
        self.bridge.interaction_requested.connect(self._resolve_interaction)

    def _run_started(self, text):
        self.agent.clear_activity()
        self.agent.add_message("You", text)

    def _runtime_event(self, event):
        if event.kind == RuntimeEventKind.MESSAGE_DELTA:
            text = ANSI_RE.sub("", str(event.payload.get("text", "")))
            self.agent.append_activity(text)
        elif event.kind in {
            RuntimeEventKind.TOOL_STARTED,
            RuntimeEventKind.TOOL_FINISHED,
            RuntimeEventKind.TOOL_FAILED,
            RuntimeEventKind.NOTICE,
            RuntimeEventKind.WARNING,
        }:
            message = event.payload.get("message") or event.payload.get("tool") or event.kind.value
            self.agent.append_activity(f"[{event.kind.value}] {message}\n")

    def _submit(self, text):
        if self.bridge.submit(text):
            self.statusBar().showMessage("Running…")

    def _run_finished(self, result):
        if result:
            self.agent.add_message("Nexgent", ANSI_RE.sub("", result))
        self.statusBar().showMessage("Ready", 2500)
        self._refresh_sessions()

    def _run_failed(self, error):
        self.agent.add_message("Error", error)
        self.statusBar().showMessage("Run failed", 5000)
        self._refresh_sessions()

    def _resolve_interaction(self, request):
        if request.kind.value == "user_input":
            if request.metadata.get("options"):
                options = request.metadata["options"]
                labels = [item.get("label", f"Option {index + 1}") for index, item in enumerate(options)]
                if request.metadata.get("multi_select"):
                    text, accepted = QInputDialog.getText(
                        self, "Nexgent question", request.prompt + "\nEnter comma-separated option numbers:"
                    )
                    if accepted:
                        try:
                            indices = [int(value.strip()) - 1 for value in text.split(",")]
                        except ValueError:
                            indices = []
                        request.resolve(bool(indices), indices)
                    else:
                        request.resolve(False)
                else:
                    item, accepted = QInputDialog.getItem(
                        self, "Nexgent question", request.prompt, labels, 0, False
                    )
                    request.resolve(accepted, labels.index(item) if accepted else None)
                return
            text, accepted = QInputDialog.getMultiLineText(
                self,
                "Nexgent input",
                request.prompt,
                request.metadata.get("placeholder", ""),
            )
            request.resolve(accepted, text)
            return
        permission = request.metadata.get("permission", "permission")
        choice = QMessageBox.question(
            self,
            f"Allow {permission}?",
            request.prompt,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        request.resolve(choice == QMessageBox.StandardButton.Yes)

    def _change_mode(self, mode):
        self.runtime.harness.perms.set_permission_mode(mode)
        self.runtime.harness.plan_mode = mode == "plan"
        self.statusBar().showMessage(f"Mode: {mode}", 2000)

    def _change_model(self, model):
        if model and model != self.runtime.harness.model:
            self._submit(f"/model set {model}")
        self.status_model.setText(model)

    def _capability_command(self, command, immediate):
        if immediate:
            self._submit(command)
        else:
            self.agent.composer.setPlainText(command)
            self.agent.composer.setFocus()
            cursor = self.agent.composer.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.agent.composer.setTextCursor(cursor)

    def _refresh_sessions(self):
        self.sessions.clear()
        files = sorted(self.runtime.session_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in files[:50]:
            self.sessions.addItem(path.stem)

    def _resume_session(self, item):
        path = self.runtime.session_dir / f"{item.text()}.jsonl"
        try:
            loaded = Session.from_jsonl(str(path)).session
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Cannot resume session", str(exc))
            return
        loaded.auto_save_dir = str(self.runtime.session_dir)
        self.runtime.session = loaded
        self.runtime.commands.session = loaded
        self.runtime.checkpoint_manager = CheckpointManager(loaded.session_id)
        self.runtime.commands.checkpoint_manager = self.runtime.checkpoint_manager
        self.runtime.harness._checkpoint_manager = self.runtime.checkpoint_manager
        self.status_session.setText(f"Session {loaded.session_id}")
        self.agent.add_message("System", f"Resumed {loaded.session_id} ({len(loaded.messages)} messages)")

    def _open_config(self):
        ConfigDialog(self.project_root, self).exec()

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.runtime.interaction_broker.set_handler(None)
        self.bridge.close()
        event.accept()
