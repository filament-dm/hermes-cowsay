# hermes-cowsay

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin that gives
your agent a `cowsay` tool: it renders text as ASCII art spoken by a cowsay
character.

## Install

This plugin has a hard dependency on the `cowsay` PyPI package, so it's
distributed as a **pip package** — the prescribed way for a third-party Hermes
plugin to depend on a Python package (pip pulls `cowsay` in automatically).
Install it into the same environment Hermes runs in:

```bash
pip install "git+https://github.com/filament-dm/hermes-cowsay"   # or: pip install hermes-cowsay
hermes plugins enable hermes-cowsay
```

Hermes auto-discovers the plugin via its `hermes_agent.plugins` entry point;
`enable` opts it in (entry-point plugins are opt-in, like directory plugins).
Plugins load at agent-process startup, so if you run the persistent gateway,
restart it to pick up the change.

> Note: `hermes plugins install <git-url>` is **not** the right command here —
> it clones the repo into `~/.hermes/plugins/` but never installs a plugin's
> Python dependencies, so `cowsay` would be missing. That command is for
> dependency-free / vendored directory plugins. Use `pip install` above.

## The tool

`cowsay(text, character="cow")`

- `text` (required) — the message the character says.
- `character` (optional) — any name in `cowsay.char_names`: `beavis`, `cheese`,
  `cow`, `daemon`, `dragon`, `fox`, `ghostbusters`, `kitty`, `meow`, `miki`,
  `milk`, `octopus`, `pig`, `stegosaurus`, `stimpy`, `trex`, `turkey`, `turtle`,
  `tux`. Defaults to `cow`. The full set is exposed as a schema `enum`, so the
  agent can pick a character by name.

So you can ask your agent to cowsay "hello world" as "ghostbusters" and it will
call `cowsay(text="hello world", character="ghostbusters")`.

## Development

```bash
uvx --with cowsay --with pytest pytest tests/ -q   # run tests
uvx ruff check .                                   # lint
```
