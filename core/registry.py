import importlib
import pkgutil
import tools as tools_pkg
from typing import Callable


def load_tools() -> tuple[dict[str, Callable], list[dict], list[dict]]:
    """
    Auto-discovers all tools in the tools/ directory.
    Each tool module must export TOOL_SCHEMA (dict) and execute (async function).

    Returns:
        tool_map: {tool_name: async execute function}
        ollama_schemas: tool schemas in Ollama format
        claude_schemas: tool schemas in Claude API format
    """
    tool_map: dict[str, Callable] = {}
    ollama_schemas: list[dict] = []
    claude_schemas: list[dict] = []

    for _, modname, _ in pkgutil.iter_modules(tools_pkg.__path__):
        # Skip private/test modules
        if modname.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"tools.{modname}")
        except Exception as e:
            print(f"[registry] skipping tools.{modname}: {e}")
            continue

        if not (hasattr(mod, "TOOL_SCHEMA") and hasattr(mod, "execute")):
            continue

        schema = mod.TOOL_SCHEMA
        name = schema["name"]
        tool_map[name] = mod.execute

        # Ollama format
        ollama_schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": schema["description"],
                "parameters": schema["parameters"],
            }
        })

        # Claude format (uses "input_schema" instead of "parameters")
        claude_schemas.append({
            "name": name,
            "description": schema["description"],
            "input_schema": schema["parameters"],
        })

    print(f"[registry] loaded {len(tool_map)} tools: {sorted(tool_map.keys())}")
    return tool_map, ollama_schemas, claude_schemas
