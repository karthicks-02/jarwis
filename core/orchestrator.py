import asyncio
import ollama
import anthropic
from typing import Callable
from core.router import keyword_route
from core.memory import Memory
import config

SYSTEM_PROMPT = """You are Jarwis, a sharp personal AI assistant inspired by Iron Man's Jarvis.
Reply in the exact same language the user speaks (Tamil, English, or mixed Tanglish).
Be concise and direct. Use tools when needed. Never say you cannot do something without trying."""

memory = Memory()
claude_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


class Orchestrator:
    def __init__(self, tool_map: dict[str, Callable], ollama_schemas: list, claude_schemas: list):
        self.tool_map = tool_map
        self.ollama_schemas = ollama_schemas
        self.claude_schemas = claude_schemas

    async def _run_tool(self, name: str, args: dict) -> str:
        fn = self.tool_map.get(name)
        if not fn:
            return f"Tool '{name}' not found"
        try:
            return str(await fn(**args))
        except Exception as e:
            return f"Tool '{name}' failed: {e}"

    async def _tier0(self, text: str) -> str | None:
        """Tier 0: keyword match — zero tokens."""
        route = keyword_route(text)
        if not route:
            return None
        action, params = route
        if action == "shutdown":
            return "SHUTDOWN"
        # Try registered tool first — allows overriding built-ins in tests
        fn = self.tool_map.get(action)
        if fn:
            return await self._run_tool(action, params)
        # Tier 0 built-ins that don't need a registered tool
        if action == "get_time":
            from datetime import datetime
            return datetime.now().strftime("%-I:%M %p")
        if action == "get_date":
            from datetime import datetime
            return datetime.now().strftime("%A, %B %-d, %Y")
        # Matched pattern but no handler registered — escalate to Tier 1
        print(f"[orchestrator] Tier 0 matched '{action}' but no handler found, escalating")
        return None

    async def _tier1_ollama(self, text: str, context: str) -> str | None:
        """Tier 1: Ollama local model — free, private."""
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\nKnown facts about the user:\n{context}"

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ]

        try:
            response = await asyncio.to_thread(
                ollama.chat,
                model=config.OLLAMA_MODEL,
                messages=messages,
                tools=self.ollama_schemas if self.ollama_schemas else None,
            )
            msg = response["message"]

            # Handle tool calls
            tool_calls = msg.get("tool_calls") or []
            if tool_calls:
                results = []
                for tc in tool_calls:
                    name = tc["function"]["name"]
                    args = tc["function"]["arguments"] or {}
                    results.append(await self._run_tool(name, args))
                return "\n".join(results)

            content = msg.get("content", "").strip()
            return content if content else None

        except Exception as e:
            print(f"[orchestrator] Ollama failed: {e}")
            return None

    async def _tier2_claude_haiku(self, text: str, context: str) -> str:
        """Tier 2: Claude Haiku — fallback, ~150 tokens, 5x cheaper than Sonnet."""
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\nKnown facts about the user:\n{context}"

        try:
            response = claude_client.messages.create(
                model=config.CLAUDE_HAIKU_MODEL,
                max_tokens=512,
                system=system,
                tools=self.claude_schemas if self.claude_schemas else [],
                messages=[{"role": "user", "content": text}],
            )

            # Handle tool use blocks
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await self._run_tool(block.name, block.input)
                    tool_results.append(result)
            if tool_results:
                return "\n".join(tool_results)

            # Text response
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    return block.text.strip()

        except Exception as e:
            print(f"[orchestrator] Claude Haiku failed: {e}")

        return "Sorry, I couldn't process that request."

    async def process(self, text: str, language: str) -> str:
        """
        Route a user request through the 3-tier hierarchy.
        Returns the response string. Always returns a string.
        """
        # Tier 0: instant keyword match
        result = await self._tier0(text)
        if result is not None:
            return result

        # Build memory context (top-k relevant facts, compact)
        facts = memory.get_top_facts(text, k=config.MEMORY_TOP_K)
        context = "\n".join(facts)

        # Tier 1: Ollama (free, local)
        result = await self._tier1_ollama(text, context)
        if result:
            memory.save_conversation(text, result, language)
            return result

        # Tier 2: Claude Haiku (fallback)
        result = await self._tier2_claude_haiku(text, context)
        memory.save_conversation(text, result, language)
        return result
