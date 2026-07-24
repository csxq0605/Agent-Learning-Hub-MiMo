import threading

from nexgent.gui.runtime_bridge import RuntimeBridge
from nexgent.runtime.interactions import InteractionBroker


class BlockingRuntime:
    def __init__(self):
        self.interaction_broker = InteractionBroker()
        self.event_sink = None
        self.calls = []
        self.guidance = []
        self.first_started = threading.Event()
        self.release_first = threading.Event()

    def set_event_sink(self, sink):
        self.event_sink = sink

    def handle_input(self, text):
        self.calls.append(text)
        if len(self.calls) == 1:
            self.first_started.set()
            self.release_first.wait(timeout=3)
        return f"done: {text}"

    def inject_guidance(self, text):
        self.guidance.append(text)

    def abort(self):
        return None

    def close(self):
        return None


def test_bridge_accepts_guidance_and_queues_next_input_while_busy(qtbot):
    runtime = BlockingRuntime()
    bridge = RuntimeBridge(runtime)
    assert bridge.submit("first")
    assert runtime.first_started.wait(timeout=1)

    with qtbot.waitSignal(bridge.guidance_injected, timeout=1000):
        assert bridge.submit("/btw use the safer path")
    assert runtime.guidance == ["use the safer path"]

    with qtbot.waitSignal(bridge.input_queued, timeout=1000):
        assert bridge.submit("second")

    runtime.release_first.set()
    qtbot.waitUntil(lambda: runtime.calls == ["first", "second"], timeout=2000)
    qtbot.waitUntil(lambda: bridge.busy is False, timeout=2000)
