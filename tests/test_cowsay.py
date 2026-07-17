"""Tests for the cowsay Hermes plugin.

The plugin only touches ``ctx`` at register time (no implicit Hermes import),
so we can import the package directly and fake the plugin context.
"""

import asyncio

import cowsay
import pytest

import hermes_cowsay


class FakeCtx:
    """Minimal stand-in for the Hermes plugin context."""

    def __init__(self):
        self.tools = {}

    def register_tool(self, *, name, toolset, schema, handler, is_async, description):
        self.tools[name] = {
            "toolset": toolset,
            "schema": schema,
            "handler": handler,
            "is_async": is_async,
            "description": description,
        }


def _run(coro):
    return asyncio.run(coro)


def test_register_exposes_cowsay_tool():
    ctx = FakeCtx()
    hermes_cowsay.register(ctx)
    assert "cowsay" in ctx.tools
    tool = ctx.tools["cowsay"]
    assert tool["is_async"] is True
    assert tool["schema"]["parameters"]["required"] == ["text"]


def test_character_enum_matches_full_char_names():
    ctx = FakeCtx()
    hermes_cowsay.register(ctx)
    params = ctx.tools["cowsay"]["schema"]["parameters"]
    enum = params["properties"]["character"]["enum"]
    assert set(enum) == set(cowsay.char_names)


def test_default_character_renders():
    out = _run(hermes_cowsay._cowsay_handler({"text": "hello world"}))
    assert "hello world" in out


def test_named_character_renders_ghostbusters():
    out = _run(
        hermes_cowsay._cowsay_handler(
            {"text": "hello world", "character": "ghostbusters"}
        )
    )
    expected = cowsay.get_output_string("ghostbusters", "hello world")
    assert out == expected


@pytest.mark.parametrize("character", sorted(cowsay.char_names))
def test_every_character_renders(character):
    out = _run(hermes_cowsay._cowsay_handler({"text": "hi", "character": character}))
    assert out == cowsay.get_output_string(character, "hi")


def test_unknown_character_is_rejected():
    out = _run(hermes_cowsay._cowsay_handler({"text": "hi", "character": "nope"}))
    assert '"error"' in out
    assert "nope" in out


def test_empty_text_is_rejected():
    out = _run(hermes_cowsay._cowsay_handler({"text": ""}))
    assert '"error"' in out
