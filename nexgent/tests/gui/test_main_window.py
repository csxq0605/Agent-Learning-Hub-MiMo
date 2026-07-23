from nexgent.gui.main_window import MainWindow
from nexgent.runtime.events import RuntimeEvent, RuntimeEventKind


def test_main_window_has_three_columns_and_control_center(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    assert window.file_tree is not None
    assert window.preview is not None
    assert window.agent is not None
    assert window.control.tabs.count() == 4


def test_capability_action_can_prefill_composer(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._capability_command("/workflow run ", False)
    assert window.agent.composer.toPlainText() == "/workflow run "


def test_mode_selector_updates_authoritative_permission_gate(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._change_mode("plan")
    assert fake_runtime.harness.perms.mode == "plan"
    assert fake_runtime.harness.plan_mode is True


def test_runtime_activity_stream_is_visible_and_ansi_free(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._run_started("inspect")
    fake_runtime.event_sink(
        RuntimeEvent(
            RuntimeEventKind.MESSAGE_DELTA,
            "console",
            {"text": "\x1b[31mtool output\x1b[0m\n"},
        )
    )
    assert window.agent.activity.isVisibleTo(window) is True
    assert window.agent.activity.toPlainText() == "tool output\n"
    assert window.agent.activity.isHidden() is False


def test_new_run_clears_previous_runtime_activity(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window.agent.append_activity("old output")
    window._run_started("new task")
    assert window.agent.activity.toPlainText() == ""
    assert window.agent.activity.isHidden() is True


def test_failed_run_updates_status_and_conversation(qtbot, fake_runtime):
    window = MainWindow(fake_runtime)
    qtbot.addWidget(window)
    window._run_failed("provider unavailable")
    assert window.statusBar().currentMessage() == "Run failed"
    assert "provider unavailable" in window.agent.messages.toPlainText()
