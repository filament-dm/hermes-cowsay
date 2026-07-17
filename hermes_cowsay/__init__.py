"""Hermes cowsay plugin — exposes a ``cowsay`` tool to the agent.

Distributed as a pip package with ``cowsay`` as a declared dependency, so pip
installs cowsay alongside it. Hermes auto-discovers the plugin through the
``hermes_agent.plugins`` entry point (see pyproject.toml) and calls
:func:`register`.

The tool renders text as ASCII art spoken by one of cowsay's characters. The
character defaults to the classic cow but may be any name in
``cowsay.char_names`` (cow, tux, dragon, ghostbusters, …), so an agent can be
asked to cowsay "hello world" as "ghostbusters".
"""

import json
import logging
from typing import Any

import cowsay

logger = logging.getLogger("hermes_cowsay")

# The full set of characters cowsay ships, sorted for a stable schema/enum.
CHAR_NAMES: list[str] = sorted(cowsay.char_names)

_DEFAULT_CHAR = "cow" if "cow" in CHAR_NAMES else CHAR_NAMES[0]

_TOOL_SCHEMA: dict = {
    "name": "cowsay",
    "description": (
        "Render text as ASCII art spoken by a cowsay character. "
        "Returns the rendered art as a plain-text string. Optionally pick "
        "a character (defaults to the classic cow) — e.g. cowsay 'hello "
        "world' as 'ghostbusters'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The message the character should say.",
            },
            "character": {
                "type": "string",
                "enum": CHAR_NAMES,
                "description": (
                    "Which cowsay character speaks the text. "
                    f"Defaults to '{_DEFAULT_CHAR}'."
                ),
            },
        },
        "required": ["text"],
    },
}


async def _cowsay_handler(args: dict, **kwargs: Any) -> str:
    """Render ``text`` with the chosen cowsay ``character``.

    cowsay is synchronous and CPU-trivial, so we call it inline. Returns
    the ASCII art on success or a JSON error object on bad input.
    """
    text = args.get("text")
    if not isinstance(text, str) or not text:
        return json.dumps({"error": "text is required and must be a non-empty string."})

    character = args.get("character") or _DEFAULT_CHAR
    if character not in CHAR_NAMES:
        return json.dumps(
            {
                "error": f"Unknown character '{character}'.",
                "available_characters": CHAR_NAMES,
            }
        )

    try:
        return cowsay.get_output_string(character, text)
    except Exception as exc:  # surface any cowsay failure to the agent
        logger.exception("hermes-cowsay: rendering failed")
        return json.dumps({"error": str(exc)})


def register(ctx: Any) -> None:
    """Hermes plugin entry point. Register the ``cowsay`` tool."""
    ctx.register_tool(
        name="cowsay",
        toolset="cowsay",
        schema=_TOOL_SCHEMA,
        handler=_cowsay_handler,
        is_async=True,
        description=_TOOL_SCHEMA["description"],
    )
    logger.info(
        "hermes-cowsay: registered cowsay tool (%d characters)", len(CHAR_NAMES)
    )
