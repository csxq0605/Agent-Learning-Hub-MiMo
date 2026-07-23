"""UI-neutral wrapper around Nexgent's authoritative slash-command dispatcher."""

from __future__ import annotations

import contextlib
import io
import shlex
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class CommandResult:
    action: str
    output: str
    session: Any


class CommandService:
    def __init__(
        self,
        harness: Any,
        session: Any,
        memory_store: Any,
        checkpoint_manager: Any = None,
        session_dir: Optional[str] = None,
    ) -> None:
        self.harness = harness
        self.session = session
        self.memory_store = memory_store
        self.checkpoint_manager = checkpoint_manager
        self.session_dir = session_dir

    def execute(self, command: str) -> CommandResult:
        from .cli import _handle_command

        parts = shlex.split(command.strip())
        if not parts:
            return CommandResult("continue", "", self.session)
        parts[0] = parts[0].lower()
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            action, session = _handle_command(
                parts,
                self.harness,
                self.session,
                self.memory_store,
                self.checkpoint_manager,
                self.session_dir,
            )
        self.session = session
        return CommandResult(action, stream.getvalue(), session)
