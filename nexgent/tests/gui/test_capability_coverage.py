from nexgent.commands import SLASH_COMMANDS
from nexgent.gui.widgets.control_center import CAPABILITIES


def test_every_command_family_is_visible_or_available_in_composer():
    top_level = {command.split()[0] for command in SLASH_COMMANDS}
    commands = {command.split()[0] for items in CAPABILITIES.values() for _, command, _ in items}
    # Basic conversation commands live in the always-visible composer/help menu;
    # every management family must also have a visible Control Center entry.
    management = {"/memory", "/hooks", "/stats", "/compact", "/context", "/init", "/init-config",
                  "/rewind", "/fork", "/subagents", "/subagent", "/parallel", "/pipeline",
                  "/agents", "/tasks", "/goal", "/skills", "/mcp", "/workflow", "/plugin"}
    assert management <= commands
    assert top_level - commands <= {"/help", "/quit", "/exit", "/q", "/clear", "/save", "/load", "/tools", "/effort", "/btw", "/model"}
