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


def test_runtime_abort_delegates_to_harness(tmp_path):
    harness = FakeHarness()
    runtime = NexgentRuntime(tmp_path, harness=harness, session=Session("test"))
    runtime.abort()
    assert harness.graceful_abort.requested
