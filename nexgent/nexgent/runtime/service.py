"""Project-scoped Nexgent runtime used by every interactive frontend."""

from __future__ import annotations

import contextlib
import io
import os
import secrets
import subprocess
from pathlib import Path
from typing import Any, Optional

from .events import RuntimeEventKind, RuntimeEventSink, emit_event
from .interactions import InteractionBroker


class _EventWriter(io.TextIOBase):
    def __init__(self, sink: Optional[RuntimeEventSink]) -> None:
        self.sink = sink
        self.parts = []

    def write(self, text: str) -> int:
        if text:
            self.parts.append(text)
            emit_event(
                self.sink,
                RuntimeEventKind.MESSAGE_DELTA,
                source="console",
                payload={"text": text},
            )
        return len(text)

    def getvalue(self) -> str:
        return "".join(self.parts)


class NexgentRuntime:
    """Own one harness, session, project, and frontend interaction channel."""

    def __init__(
        self,
        project_root: os.PathLike[str] | str,
        *,
        harness: Any = None,
        session: Any = None,
        event_sink: Optional[RuntimeEventSink] = None,
        interaction_broker: Optional[InteractionBroker] = None,
        agent_options: Optional[dict] = None,
    ) -> None:
        from ..agent import NexgentAgent
        from ..command_service import CommandService
        from ..context import CheckpointManager, Session
        from ..memory import MemoryStore
        from ..models import get_model_registry

        self.project_root = Path(project_root).expanduser().resolve()
        self.session_dir = self.project_root / ".nexgent" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.event_sink = event_sink
        self.interaction_broker = interaction_broker or InteractionBroker()
        registry = get_model_registry()
        project_models = self.project_root / "models.json"
        registry.reload(str(project_models) if project_models.exists() else None)
        options = dict(agent_options or {})
        if harness is None and "model" not in options:
            options["model"] = registry.get_default("main").model_name
        self.harness = harness or NexgentAgent(**options)
        self.last_command_action = "continue"
        self.harness._runtime_event_callback = self._on_harness_event
        self.harness._subagent_event_callback = self._on_subagent_event
        self.harness._subagent_session_dir = str(self.session_dir / "agents")
        existing_subagent_manager = getattr(self.harness, "_subagent_manager", None)
        if existing_subagent_manager is not None:
            existing_subagent_manager.event_callback = self._on_subagent_event
            existing_subagent_manager.session_dir = self.harness._subagent_session_dir
        self.session = session or Session(
            secrets.token_hex(4),
            auto_save_dir=str(self.session_dir),
            working_dir=str(self.project_root),
        )
        self.session.auto_save_dir = str(self.session_dir)
        self.checkpoint_manager = CheckpointManager(self.session.session_id)
        self.harness._checkpoint_manager = self.checkpoint_manager
        if hasattr(self.harness.perms, "set_interaction_broker"):
            self.harness.perms.set_interaction_broker(self.interaction_broker)
        self.harness.interaction_broker = self.interaction_broker
        self.memory_store = MemoryStore(str(self.project_root))
        self.commands = CommandService(
            self.harness,
            self.session,
            self.memory_store,
            self.checkpoint_manager,
            str(self.session_dir),
        )

    def set_event_sink(self, sink: Optional[RuntimeEventSink]) -> None:
        self.event_sink = sink

    def _emit(self, kind: RuntimeEventKind, **payload: Any) -> None:
        emit_event(self.event_sink, kind, source="runtime", payload=payload)

    def _on_subagent_event(self, payload: dict[str, Any]) -> None:
        subagent_id = str(payload.get("subagent_id") or "unknown")
        event_kind = payload.get("event_kind")
        if event_kind:
            event_payload = {
                key: value
                for key, value in payload.items()
                if key not in {"event_kind", "subagent_id", "state", "task", "description"}
            }
            emit_event(
                self.event_sink,
                RuntimeEventKind(str(event_kind)),
                source=f"subagent:{subagent_id}",
                payload=event_payload,
            )
            return
        emit_event(
            self.event_sink,
            RuntimeEventKind.SUBAGENT_CHANGED,
            source=f"subagent:{subagent_id}",
            payload=payload,
        )

    def _on_harness_event(self, kind: str, payload: dict[str, Any]) -> None:
        emit_event(
            self.event_sink,
            RuntimeEventKind(kind),
            source="main",
            payload=payload,
        )

    def inject_guidance(self, text: str) -> None:
        """Inject user guidance into the active session without starting a new run."""
        value = text.strip()
        if not value:
            return
        self.session.add_message("user", value, injected=True)
        self._emit(RuntimeEventKind.NOTICE, message=f"Guidance injected: {value}")

    def handle_input(self, text: str) -> str:
        value = text.strip()
        if not value:
            return ""
        self.last_command_action = "continue"
        self._emit(RuntimeEventKind.RUN_STARTED, text=value)
        writer = _EventWriter(self.event_sink)
        from ..tools.interactive import set_interaction_broker
        from ..skills import SkillSubstitutor
        set_interaction_broker(self.interaction_broker)
        SkillSubstitutor.set_interaction_broker(self.interaction_broker)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                if value.startswith("/"):
                    result = self._handle_interactive_command(value)
                elif value.startswith("!"):
                    result = self._run_shell(value[1:])
                else:
                    from ..file_references import FileReferenceResolver
                    prompt = FileReferenceResolver.resolve_and_format(value, str(self.project_root))
                    previous = Path.cwd()
                    try:
                        os.chdir(self.project_root)
                        result = self.harness.run(prompt, self.session)
                    finally:
                        os.chdir(previous)
            self._emit(
                RuntimeEventKind.RUN_FINISHED,
                result=result or "",
                session_id=self.session.session_id,
                messages=len(self.session.messages),
            )
            return result or writer.getvalue()
        except Exception as exc:
            self._emit(RuntimeEventKind.ERROR, message=str(exc), exception=type(exc).__name__)
            raise
        finally:
            set_interaction_broker(None)
            SkillSubstitutor.set_interaction_broker(None)

    def _handle_interactive_command(self, value: str) -> str:
        """Resolve commands whose CLI implementation reads from stdin."""
        import shlex
        from .interactions import InteractionKind, InteractionRequest

        parts = shlex.split(value)
        if parts and parts[0].lower() == "/remember":
            response = self.interaction_broker.request(InteractionRequest(
                InteractionKind.USER_INPUT,
                "Save project memory",
                {"multiline": True, "placeholder": "Context Nexgent should remember"},
            ))
            if not response.accepted or not str(response.value or "").strip():
                return "Memory creation cancelled."
            from ..memory import MemoryType
            name = f"session-{self.session.session_id[:8]}"
            self.memory_store.save_memory(
                name=name,
                memory_type=MemoryType.PROJECT,
                description=f"Memory from session {self.session.session_id[:8]}",
                content=str(response.value).strip(),
            )
            return f"Memory saved: {name}"

        if parts and parts[0].lower() == "/init" and (self.project_root / "AGENTS.md").exists():
            response = self.interaction_broker.request(InteractionRequest(
                InteractionKind.PERMISSION,
                "AGENTS.md already exists. Overwrite it?",
                {"permission": "write", "path": str(self.project_root / "AGENTS.md")},
            ))
            if not response.accepted:
                return "Project initialization skipped."
            from ..project_scanner import generate_agents_md, scan_project
            result = scan_project(str(self.project_root))
            destination = self.project_root / "AGENTS.md"
            destination.write_text(generate_agents_md(result), encoding="utf-8")
            return f"AGENTS.md generated at {destination}"

        if len(parts) >= 4 and parts[:2] == ["/agents", "create"]:
            name = parts[2]
            description = " ".join(parts[3:])
            response = self.interaction_broker.request(InteractionRequest(
                InteractionKind.USER_INPUT,
                f"System prompt for Agent '{name}'",
                {"multiline": True, "placeholder": f"You are {name}."},
            ))
            if not response.accepted:
                return "Agent creation cancelled."
            from ..agents import AgentManager
            manager = getattr(self.harness, "_agent_manager", None) or AgentManager(str(self.project_root))
            self.harness._agent_manager = manager
            prompt = str(response.value or "").strip() or f"You are {name}."
            path = manager.create_agent(name, description, prompt)
            return f"Agent '{name}' created at {path}"

        command_result = self.commands.execute(value)
        self.last_command_action = command_result.action
        self.session = command_result.session
        self.commands.session = self.session
        return command_result.output

    def _run_shell(self, command: str) -> str:
        from ..permissions import Permission
        from ..tools.shell import _is_readonly, _scrub_env

        permission = Permission.READ if _is_readonly(command) else Permission.WRITE
        if not self.harness.perms.check(
            permission, f"run_command({command[:100]})", {"command": command}
        ):
            return "[blocked by permission system]"
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=self.project_root,
            env=_scrub_env(),
        )
        return (completed.stdout or "") + (completed.stderr or "")

    def abort(self) -> None:
        self.harness.graceful_abort.request()
        manager = getattr(self.harness, "_subagent_manager", None)
        if manager is not None:
            manager.cancel_all()
        self._emit(RuntimeEventKind.RUN_ABORTED)

    def close(self) -> None:
        try:
            self.session.save_meta_to_jsonl()
        except OSError:
            pass
        self.interaction_broker.set_handler(None)
        try:
            from ..tools.interactive import set_interaction_broker
            set_interaction_broker(None)
            from ..skills import SkillSubstitutor
            SkillSubstitutor.set_interaction_broker(None)
        except Exception:
            pass
        try:
            from ..tools.scheduler_tools import get_scheduler
            scheduler = get_scheduler()
            if scheduler:
                scheduler.stop()
        except Exception:
            pass
