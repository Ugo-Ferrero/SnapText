# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Mon Text Blaze" is a macOS text-expander daemon. It listens to global keyboard input, detects configured shortcuts, and replaces them with their full-text expansions (like the Text Blaze browser extension, but system-wide).

- `daemon.py` — the main process: listens to keyboard events, matches shortcuts, and pastes expansions
- `snippets.json` — maps shortcut strings to their replacement text
- `.venv/` — local Python virtualenv

## Running

```bash
# Activate venv first, or prefix with .venv/bin/python3
.venv/bin/python3 daemon.py
```

macOS requires **Accessibility permission** for the terminal app running the daemon (System Settings → Privacy & Security → Accessibility).

## Dependencies

Install into the venv:
```bash
.venv/bin/pip install pyperclip pynput
```

## Architecture

`daemon.py` uses `pynput.keyboard.Listener` to capture all keystrokes globally. A rolling `buffer` (max 50 chars) accumulates typed characters. After each printable keystroke, `verifier_buffer()` checks if the buffer ends with any key in `snippets`. On a match, `effacer_et_coller()` sends `Backspace` × len(shortcut), copies the replacement to the clipboard via `pyperclip`, then pastes with `Cmd+V`.

Special keys: space is appended to the buffer, backspace pops it, enter/other specials clear it.
