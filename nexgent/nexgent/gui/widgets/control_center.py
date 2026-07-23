from collections import OrderedDict

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QLabel, QPushButton, QScrollArea, QTabWidget,
    QVBoxLayout, QWidget,
)


CAPABILITIES = OrderedDict([
    ("Run", [
        ("Tasks", "/tasks list", True), ("Task details", "/tasks show ", False),
        ("Cancel task", "/tasks cancel ", False), ("Clean tasks", "/tasks cleanup", True),
        ("SubAgents", "/subagents", True), ("Run SubAgent", "/subagent ", False),
        ("Parallel", "/parallel task one | task two", False), ("Pipeline", "/pipeline stage one | stage two", False),
    ]),
    ("Automate", [
        ("Workflow runs", "/workflow list", True), ("Run workflow", "/workflow run ", False),
        ("Workflow status", "/workflow status ", False), ("Resume workflow", "/workflow resume ", False),
        ("Save workflow", "/workflow save ", False), ("Goal status", "/goal", True),
        ("Set goal", "/goal ", False), ("Clear goal", "/goal clear", True),
    ]),
    ("Extensions", [
        ("MCP status", "/mcp", True), ("Install MCP", "/mcp install ", False),
        ("Connect MCP", "/mcp connect ", False), ("Disconnect MCP", "/mcp disconnect ", False),
        ("Refresh MCP", "/mcp refresh", True), ("Plugins", "/plugin list", True),
        ("Load plugin", "/plugin load ", False), ("Unload plugin", "/plugin unload ", False),
        ("Install plugin", "/plugin install ", False), ("Skills", "/skills", True),
        ("Install skill", "/skills install ", False), ("Agents", "/agents list", True),
        ("Create agent", "/agents create ", False), ("Show agent", "/agents show ", False),
        ("Delete agent", "/agents delete ", False), ("Hooks", "/hooks", True),
    ]),
    ("State", [
        ("Memory", "/memory", True), ("Remember", "/remember", False),
        ("Checkpoints", "/rewind", False), ("Fork session", "/fork", True),
        ("Session stats", "/stats", True), ("Context", "/context", True),
        ("Compact", "/compact", True), ("Tools", "/tools", True),
        ("Save session", "/save ", False), ("Load session", "/load ", False),
        ("Project init", "/init", False), ("Global config", "/init-config", False),
    ]),
])


class CapabilityPage(QScrollArea):
    command_requested = pyqtSignal(str, bool)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        host = QWidget()
        grid = QGridLayout(host)
        for index, (label, command, immediate) in enumerate(items):
            button = QPushButton(label)
            button.setToolTip(command)
            button.clicked.connect(lambda _=False, c=command, i=immediate: self.command_requested.emit(c, i))
            grid.addWidget(button, index // 4, index % 4)
        grid.setRowStretch((len(items) + 3) // 4, 1)
        self.setWidget(host)


class ControlCenter(QFrame):
    command_requested = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        title = QLabel("CONTROL CENTER")
        title.setObjectName("Section")
        layout.addWidget(title)
        self.tabs = QTabWidget()
        for name, items in CAPABILITIES.items():
            page = CapabilityPage(items)
            page.command_requested.connect(self.command_requested)
            self.tabs.addTab(page, name)
        layout.addWidget(self.tabs)
