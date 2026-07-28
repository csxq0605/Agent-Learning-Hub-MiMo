from nexgent.context import Session
from nexgent.runtime.events import RuntimeEventKind
from nexgent.runtime.service import NexgentRuntime


class FakeAbort:
    def request(self):
        self.requested = True


class FakePerms:
    def set_interaction_broker(self, broker):
        self.broker = broker


class FakeHarness:
    def __init__(self):
        self.model = "fake-model"
        self.graceful_abort = FakeAbort()
        self.perms = FakePerms()

    def run(self, text, session):
        print("tool activity")
        session.add_message("user", text)
        session.add_message("assistant", "answer")
        return "answer"


def test_runtime_runs_prompt_and_emits_lifecycle(tmp_path):
    events = []
    runtime = NexgentRuntime(
        project_root=tmp_path,
        harness=FakeHarness(),
        session=Session("test", auto_save_dir=str(tmp_path)),
        event_sink=events.append,
    )
    result = runtime.handle_input("hello")
    assert result == "answer"
    assert events[0].kind is RuntimeEventKind.RUN_STARTED
    assert any(e.kind is RuntimeEventKind.MESSAGE_DELTA for e in events)
    assert events[-1].kind is RuntimeEventKind.RUN_FINISHED


def test_runtime_preserves_quit_command_action(tmp_path):
    runtime = NexgentRuntime(
        project_root=tmp_path,
        harness=FakeHarness(),
        session=Session("test", auto_save_dir=str(tmp_path)),
    )
    result = runtime.handle_input("/quit")
    assert runtime.last_command_action == "quit"
    assert "Bye!" in result


def test_runtime_abort_delegates_to_harness(tmp_path):
    harness = FakeHarness()
    runtime = NexgentRuntime(tmp_path, harness=harness, session=Session("test"))
    runtime.abort()
    assert harness.graceful_abort.requested


def test_runtime_abort_also_cancels_active_subagents(tmp_path):
    class Manager:
        def __init__(self):
            self.cancelled = False

        def cancel_all(self):
            self.cancelled = True

    harness = FakeHarness()
    harness._subagent_manager = Manager()
    runtime = NexgentRuntime(tmp_path, harness=harness, session=Session("test"))
    runtime.abort()
    assert harness.graceful_abort.requested
    assert harness._subagent_manager.cancelled


def test_runtime_turns_subagent_callback_into_typed_event(tmp_path):
    events = []
    harness = FakeHarness()
    harness._subagent_manager = None
    NexgentRuntime(
        tmp_path,
        harness=harness,
        session=Session("test"),
        event_sink=events.append,
    )
    harness._subagent_event_callback(
        {"subagent_id": "child-1", "state": "running", "task": "inspect"}
    )
    event = events[-1]
    assert event.kind is RuntimeEventKind.SUBAGENT_CHANGED
    assert event.source == "subagent:child-1"
    assert event.payload["task"] == "inspect"


def test_runtime_routes_structured_harness_tool_event(tmp_path):
    events = []
    harness = FakeHarness()
    NexgentRuntime(
        tmp_path,
        harness=harness,
        session=Session("test"),
        event_sink=events.append,
    )
    harness._runtime_event_callback(
        "tool_started", {"tool": "read_file", "arguments": {"path": "README.md"}}
    )
    event = events[-1]
    assert event.kind is RuntimeEventKind.TOOL_STARTED
    assert event.source == "main"
    assert event.payload["tool"] == "read_file"


def test_runtime_routes_subagent_tool_event_to_subagent_source(tmp_path):
    events = []
    harness = FakeHarness()
    NexgentRuntime(
        tmp_path,
        harness=harness,
        session=Session("test"),
        event_sink=events.append,
    )
    harness._subagent_event_callback({
        "subagent_id": "child-1",
        "state": "running",
        "task": "inspect",
        "event_kind": "tool_finished",
        "tool": "read_file",
        "message": "README.md",
    })
    event = events[-1]
    assert event.kind is RuntimeEventKind.TOOL_FINISHED
    assert event.source == "subagent:child-1"
    assert event.payload["tool"] == "read_file"


def test_runtime_inject_guidance_persists_in_active_session(tmp_path):
    events = []
    session = Session("test")
    runtime = NexgentRuntime(
        tmp_path,
        harness=FakeHarness(),
        session=session,
        event_sink=events.append,
    )
    runtime.inject_guidance("use the safer path")
    assert session.messages[-1] == {
        "role": "user",
        "content": "use the safer path",
        "injected": True,
    }
    assert events[-1].kind is RuntimeEventKind.NOTICE
