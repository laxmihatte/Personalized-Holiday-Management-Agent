"""Test configuration.

Makes the suite hermetic: if the heavy `autogen` packages aren't installed
(e.g. a lightweight CI lane), we stub the few symbols the app imports so tests
run without external dependencies or an API key. When autogen *is* installed,
the real modules are used and these stubs are skipped.
"""
import sys
import types


def _ensure_module(name: str) -> types.ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    module = types.ModuleType(name)
    sys.modules[name] = module
    # register as attribute on parent package so `from pkg.sub import x` works
    if "." in name:
        parent, child = name.rsplit(".", 1)
        setattr(_ensure_module(parent), child, module)
    return module


def _stub_autogen_if_missing() -> None:
    try:
        import autogen_agentchat.messages  # noqa: F401
        import autogen_ext.models.openai  # noqa: F401
        return  # real packages available, nothing to stub
    except Exception:
        pass

    messages = _ensure_module("autogen_agentchat.messages")

    class TextMessage:
        def __init__(self, content="", source="User"):
            self.content = content
            self.source = source

    messages.TextMessage = TextMessage

    agents = _ensure_module("autogen_agentchat.agents")
    agents.AssistantAgent = lambda *a, **k: object()

    teams = _ensure_module("autogen_agentchat.teams")
    teams.RoundRobinGroupChat = lambda *a, **k: object()

    conditions = _ensure_module("autogen_agentchat.conditions")
    conditions.TextMentionTermination = lambda *a, **k: object()
    conditions.MaxMessageTermination = lambda *a, **k: object()

    openai_mod = _ensure_module("autogen_ext.models.openai")
    openai_mod.OpenAIChatCompletionClient = lambda *a, **k: object()


_stub_autogen_if_missing()
