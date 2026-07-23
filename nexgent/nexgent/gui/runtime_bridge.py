"""The only Qt-to-runtime boundary."""

from __future__ import annotations

import threading

from PyQt6.QtCore import QObject, pyqtSignal

from ..runtime.events import RuntimeEvent


class RuntimeBridge(QObject):
    event_received = pyqtSignal(object)
    interaction_requested = pyqtSignal(object)
    run_started = pyqtSignal(str)
    run_finished = pyqtSignal(str)
    run_failed = pyqtSignal(str)
    busy_changed = pyqtSignal(bool)

    def __init__(self, runtime, parent=None):
        super().__init__(parent)
        self.runtime = runtime
        self._busy = False
        runtime.set_event_sink(self._on_event)
        runtime.interaction_broker.set_handler(self._on_interaction)

    @property
    def busy(self):
        return self._busy

    def submit(self, text: str) -> bool:
        if self._busy or not text.strip():
            return False
        self._busy = True
        self.busy_changed.emit(True)
        self.run_started.emit(text)
        threading.Thread(target=self._run, args=(text,), daemon=True).start()
        return True

    def _run(self, text: str) -> None:
        try:
            result = self.runtime.handle_input(text)
            self.run_finished.emit(result)
        except Exception as exc:
            self.run_failed.emit(str(exc))
        finally:
            self._busy = False
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
