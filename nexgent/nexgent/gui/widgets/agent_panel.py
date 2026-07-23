from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
    QTextBrowser, QVBoxLayout,
)


class Composer(QPlainTextEdit):
    submitted = pyqtSignal(str)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            text = self.toPlainText().strip()
            if text:
                self.submitted.emit(text)
                self.clear()
            return
        super().keyPressEvent(event)


class AgentPanel(QFrame):
    submitted = pyqtSignal(str)
    stop_requested = pyqtSignal()
    mode_changed = pyqtSignal(str)

    def __init__(self, model: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        header = QHBoxLayout()
        title = QLabel("AGENT")
        title.setObjectName("Section")
        self.status = QLabel("Ready")
        self.status.setObjectName("Muted")
        self.model = QComboBox()
        self.model.addItem(model)
        self.mode = QComboBox()
        self.mode.addItems(["default", "plan", "accept_edits", "auto", "dont_ask", "bypass"])
        self.mode.currentTextChanged.connect(self.mode_changed)
        header.addWidget(title)
        header.addWidget(self.status)
        header.addStretch()
        header.addWidget(self.model)
        header.addWidget(self.mode)
        layout.addLayout(header)
        self.messages = QTextBrowser()
        self.messages.setOpenExternalLinks(True)
        layout.addWidget(self.messages, 1)
        self.activity_label = QLabel("RUNTIME ACTIVITY")
        self.activity_label.setObjectName("Section")
        self.activity_label.setVisible(False)
        layout.addWidget(self.activity_label)
        self.activity = QPlainTextEdit()
        self.activity.setObjectName("RuntimeActivity")
        self.activity.setReadOnly(True)
        self.activity.setMaximumBlockCount(1000)
        self.activity.setMaximumHeight(130)
        self.activity.setVisible(False)
        layout.addWidget(self.activity)
        self.composer = Composer()
        self.composer.setPlaceholderText("Ask Nexgent…  / for commands · @ for files · Shift+Enter for newline")
        self.composer.setMaximumHeight(110)
        self.composer.submitted.connect(self.submitted)
        layout.addWidget(self.composer)
        actions = QHBoxLayout()
        self.stop = QPushButton("Stop")
        self.stop.setObjectName("Danger")
        self.stop.setEnabled(False)
        self.stop.clicked.connect(self.stop_requested)
        send = QPushButton("Send")
        send.setObjectName("Primary")
        send.clicked.connect(lambda: self.composer.submitted.emit(self.composer.toPlainText().strip()) if self.composer.toPlainText().strip() else None)
        actions.addWidget(self.stop)
        actions.addStretch()
        actions.addWidget(send)
        layout.addLayout(actions)

    def add_message(self, role: str, text: str):
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        color = {"You": "#4B63FF", "Nexgent": "#171D3B", "System": "#6F7890", "Error": "#D92D20"}.get(role, "#273044")
        self.messages.append(f'<div><b style="color:{color}">{role}</b><br><span style="white-space:pre-wrap">{safe}</span></div>')
        self.messages.ensureCursorVisible()

    def set_busy(self, busy: bool):
        self.status.setText("Running" if busy else "Ready")
        self.stop.setEnabled(busy)
        self.composer.setEnabled(not busy)

    def clear_activity(self):
        self.activity.clear()
        self.activity.setVisible(False)
        self.activity_label.setVisible(False)

    def append_activity(self, text: str):
        if not text:
            return
        self.activity_label.setVisible(True)
        self.activity.setVisible(True)
        cursor = self.activity.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.activity.setTextCursor(cursor)
        self.activity.ensureCursorVisible()
