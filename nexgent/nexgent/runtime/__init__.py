"""Frontend-neutral runtime contracts for Nexgent."""

from .events import RuntimeEvent, RuntimeEventKind, emit_event
from .interactions import (
    InteractionBroker,
    InteractionKind,
    InteractionRequest,
    InteractionResponse,
)
from .service import NexgentRuntime

__all__ = [
    "InteractionBroker",
    "InteractionKind",
    "InteractionRequest",
    "InteractionResponse",
    "NexgentRuntime",
    "RuntimeEvent",
    "RuntimeEventKind",
    "emit_event",
]
