from PyQt6.QtCore import Qt

from nexgent.gui.main_window import MainWindow
from nexgent.gui.widgets.agent_panel import Composer
from nexgent.runtime.events import RuntimeEvent, RuntimeEventKind


def set_composer_text(composer, text):
    composer.setPlainText(text)
    cursor = composer.textCursor()
    cursor.movePosition(cursor.MoveOperation.End)
    composer.setTextCursor(cursor)
    composer._update_completions()


def test_main_window_is_compact_and_has_no_control_center(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    assert window.file_tree is not None
    assert window.preview is not None
    assert window.agent is not None
    assert window.navigation_tabs.count() == 3
    assert not hasattr(window, "control")
    assert not hasattr(window.agent, "activity")


def test_mode_selector_updates_authoritative_permission_gate(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._change_mode("plan")
    assert fake_runtime.harness.perms.mode == "plan"
    assert fake_runtime.harness.plan_mode is True


def test_runtime_activity_is_folded_into_conversation_and_ansi_free(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window.show()
    window._run_started("inspect")
    fake_runtime.event_sink(
        RuntimeEvent(
            RuntimeEventKind.MESSAGE_DELTA,
            "console",
            {"text": "\x1b[31mtool output\x1b[0m\n"},
        )
    )
    assert "tool output" in window.agent.messages.toPlainText()
    assert "\x1b" not in window.agent.messages.toPlainText()


def test_long_tool_result_is_compact_in_conversation(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._runtime_event(
        RuntimeEvent(
            RuntimeEventKind.TOOL_FINISHED,
            "main",
            {"tool": "read_file", "message": "result " * 100},
        )
    )
    text = window.agent.messages.toPlainText()
    assert "✓ read_file" in text
    assert text.endswith("…")
    assert len(text) < 200


def test_new_run_preserves_unified_conversation(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window.agent.append_activity("old output")
    window._run_started("new task")
    text = window.agent.messages.toPlainText()
    assert "old output" in text
    assert "new task" in text


def test_failed_run_updates_status_and_conversation(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._run_failed("provider unavailable")
    assert window.statusBar().currentMessage() == "Run failed"
    assert "provider unavailable" in window.agent.messages.toPlainText()


def test_subagent_event_creates_switchable_agent_conversation(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._runtime_event(
        RuntimeEvent(
            RuntimeEventKind.SUBAGENT_CHANGED,
            "subagent:abc123",
            {
                "subagent_id": "abc123",
                "state": "created",
                "description": "Review the GUI",
            },
        )
    )
    window._runtime_event(
        RuntimeEvent(
            RuntimeEventKind.TOOL_FINISHED,
            "subagent:abc123",
            {"tool": "read_file", "message": "main_window.py"},
        )
    )
    window._runtime_event(
        RuntimeEvent(
            RuntimeEventKind.SUBAGENT_CHANGED,
            "subagent:abc123",
            {
                "subagent_id": "abc123",
                "state": "completed",
                "result": "Review complete",
            },
        )
    )
    assert window.agent_list.count() == 2
    window.agent_list.setCurrentRow(1)
    assert window.agent.current_agent_id == "abc123"
    assert window.agent.status.text() == "Completed"
    assert "Review the GUI" in window.agent.messages.toPlainText()
    assert "read_file" in window.agent.messages.toPlainText()
    assert "Review complete" in window.agent.messages.toPlainText()


def test_composer_slash_popup_and_tab_completion(qtbot, tmp_path):
    composer = Composer(tmp_path)
    qtbot.addWidget(composer)
    composer.show()
    composer.setFocus()
    set_composer_text(composer, "/workf")
    assert "/workflow" in composer.completion_candidates
    qtbot.keyClick(composer, Qt.Key.Key_Tab)
    assert composer.toPlainText() == "/workflow"


def test_composer_at_popup_and_tab_completion(qtbot, tmp_path):
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    composer = Composer(tmp_path)
    qtbot.addWidget(composer)
    composer.show()
    composer.setFocus()
    set_composer_text(composer, "Inspect @READ")
    assert "README.md" in composer.completion_candidates
    qtbot.keyClick(composer, Qt.Key.Key_Tab)
    assert composer.toPlainText() == "Inspect @README.md"


def test_composer_up_down_restores_persisted_history_and_draft(qtbot, tmp_path):
    composer = Composer(tmp_path)
    qtbot.addWidget(composer)
    submitted = []
    composer.submitted.connect(submitted.append)
    composer.setPlainText("first")
    assert composer.submit_current()
    composer.setPlainText("second")
    assert composer.submit_current()
    composer.setPlainText("draft")

    qtbot.keyClick(composer, Qt.Key.Key_Up)
    assert composer.toPlainText() == "second"
    qtbot.keyClick(composer, Qt.Key.Key_Up)
    assert composer.toPlainText() == "first"
    qtbot.keyClick(composer, Qt.Key.Key_Down)
    assert composer.toPlainText() == "second"
    qtbot.keyClick(composer, Qt.Key.Key_Down)
    assert composer.toPlainText() == "draft"
    assert submitted == ["first", "second"]
    assert (tmp_path / ".nexgent" / "input_history.json").is_file()

    reopened = Composer(tmp_path)
    qtbot.addWidget(reopened)
    qtbot.keyClick(reopened, Qt.Key.Key_Up)
    assert reopened.toPlainText() == "second"
