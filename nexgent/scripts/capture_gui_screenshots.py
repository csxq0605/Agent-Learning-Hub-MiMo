"""Capture a sanitized, repeatable Nexgent desktop screenshot."""

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QTimer

from nexgent.gui.app import create_application
from nexgent.gui.main_window import MainWindow
from nexgent.runtime.service import NexgentRuntime
from nexgent.context import Session


def main():
    app = create_application(["nexgent-screenshot"])
    runtime = NexgentRuntime(
        ROOT / "demo-project",
        session=Session("demo-session"),
        agent_options={"model": "mimo-v2.5-pro", "auto_approve": True},
    )
    window = MainWindow(runtime)
    window.agent.add_message("You", "Review the authentication service and run its tests.")
    window.agent.add_message(
        "Nexgent",
        "I’ll inspect the project instructions, trace the authentication flow, and report verified findings.",
    )
    window.agent.append_activity(
        "→ Read AGENTS.md\n→ Search authentication routes\n✓ 42 tests passed\n"
    )
    window.preview.text.setMarkdown(
        "# Authentication review\n\n**Status:** running\n\n- Project context loaded\n- Test suite discovered\n- Security review queued"
    )
    window.preview.setCurrentWidget(window.preview.text)
    window.control.tabs.setCurrentIndex(2)
    window.sessions.clear()
    window.sessions.addItem("demo-session")
    window.show()
    app.processEvents()

    destination = ROOT / "assets" / "screenshots" / "main-window.png"
    destination.parent.mkdir(parents=True, exist_ok=True)

    def capture():
        window.repaint()
        app.processEvents()
        window.grab().save(str(destination), "PNG")
        runtime.session.auto_save_dir = None
        window.close()
        app.quit()

    QTimer.singleShot(1500, capture)
    app.exec()


if __name__ == "__main__":
    main()
