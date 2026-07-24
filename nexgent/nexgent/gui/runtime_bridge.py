"""The only Qt-to-runtime boundary."""

from __future__ import annotations

import threading
from collections import deque

from PyQt6.QtCore import QObject, pyqtSignal

from ..runtime.events import RuntimeEvent


class RuntimeBridge(QObject):
    event_received = pyqtSignal(object)
    interaction_requested = pyqtSignal(object)
    run_started = pyqtSignal(str)
    run_finished = pyqtSignal(str)
    run_failed = pyqtSignal(str)
    busy_changed = pyqtSignal(bool)
    input_queued = pyqtSignal(str, int)
    guidance_injected = pyqtSignal(str)

    def __init__(self, runtime, parent=None):
        super().__init__(parent)
        self.runtime = runtime
        self._busy = False
        self._state_lock = threading.Lock()
        self._pending = deque(maxlen=20)
        runtime.set_event_sink(self._on_event)
        runtime.interaction_broker.set_handler(self._on_interaction)

    @property
    def busy(self):
        return self._busy

    def submit(self, text: str) -> bool:
        value = text.strip()
        if not value:
            return False
        with self._state_lock:
            if self._busy:
                if value == "/btw" or value.startswith("/btw "):
                    guidance = value[4:].strip()
                    if not guidance:
                        return False
                    self.runtime.inject_guidance(guidance)
                    self.guidance_injected.emit(guidance)
                    return True
                if len(self._pending) >= self._pending.maxlen:
                    return False
                self._pending.append(value)
                self.input_queued.emit(value, len(self._pending))
                return True
            self._busy = True
        self.busy_changed.emit(True)
        self.run_started.emit(value)
        threading.Thread(target=self._run, args=(value,), daemon=True).start()
        return True

    def _run(self, text: str) -> None:
        try:
            result = self.runtime.handle_input(text)
            self.run_finished.emit(result)
        except Exception as exc:
            self.run_failed.emit(str(exc))
        finally:
            with self._state_lock:
                next_input = self._pending.popleft() if self._pending else None
                self._busy = bool(next_input)
            if next_input:
                self.run_started.emit(next_input)
                threading.Thread(
                    target=self._run, args=(next_input,), daemon=True
                ).start()
            else:
                self.busy_changed.emit(False)

    def _on_event(self, event: RuntimeEvent) -> None:
        self.event_received.emit(event)

    def _on_interaction(self, request):
        self.interaction_requested.emit(request)
        return None

    def abort(self) -> None:
        self.runtime.abort()

    def close(self) -> None:
        self.runtime.close()
