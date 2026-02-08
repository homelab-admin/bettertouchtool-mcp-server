"""
BTT documentation reference lookup tool.

Provides access to BTT trigger, action, CLI, and variable documentation
so the LLM can construct accurate JSON for trigger/action creation.
"""

import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from btt_mcp.server import mcp

DOCS_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "btt"

# Map of doc files to load
DOC_FILES = {
    "triggers": "btt_trigger_docs.md",
    "cli": "btt_cli_docs.md",
    "variables": "btt_vars_docs.md",
    "actions": "btt_cli_actions_docs.md",
}

# Section index: maps topic keywords to (file_key, section_heading) pairs.
# This lets us return just the relevant portion of the docs.
SECTION_INDEX: list[tuple[list[str], str, str]] = [
    # (keywords, file_key, section_heading_pattern)
    # Trigger structure
    (
        ["trigger structure", "required fields", "basic trigger", "trigger json"],
        "triggers",
        r"^# BetterTouchTool Trigger JSON Reference$",
    ),
    (
        ["named trigger", "reusable trigger", "named"],
        "triggers",
        r"^### 3\.\s*Other Triggers",
    ),
    (
        ["keyboard shortcut", "keyboard", "shortcut", "hotkey", "key combo"],
        "triggers",
        r"^### 4\.\s*Keyboard Shortcuts",
    ),
    (
        ["key sequence", "typed word", "key seq"],
        "triggers",
        r"^### 5\.\s*Key Sequences",
    ),
    (
        ["trackpad", "gesture", "swipe", "pinch", "tap"],
        "triggers",
        r"^### 1\.\s*Trackpad Gestures",
    ),
    (
        ["magic mouse", "mouse gesture"],
        "triggers",
        r"^### 2\.\s*Magic Mouse",
    ),
    (
        ["touch bar", "touchbar"],
        "triggers",
        r"^### 9\.\s*Touch Bar",
    ),
    (
        ["stream deck", "streamdeck"],
        "triggers",
        r"^### 10\.\s*Stream Deck",
    ),
    (
        ["notch bar", "notchbar"],
        "triggers",
        r"^### 11\.\s*Notch Bar",
    ),
    (
        ["floating menu", "menu item"],
        "triggers",
        r"^### 12\.\s*Floating Menu",
    ),
    (
        ["midi"],
        "triggers",
        r"^### 13\.\s*MIDI",
    ),
    (
        ["siri remote", "apple tv remote"],
        "triggers",
        r"^### 8\.\s*Siri Remote",
    ),
    (
        ["drawing"],
        "triggers",
        r"^### 6\.\s*Drawings",
    ),
    (
        ["modifier", "modifier key", "command", "option", "control", "shift"],
        "triggers",
        r"^### Modifier Keys",
    ),
    (
        ["color", "rgba", "icon", "sf symbol"],
        "triggers",
        r"^## Special Configurations",
    ),
    (
        ["example", "complete example", "sample"],
        "triggers",
        r"^## Complete Examples",
    ),
    (
        ["tips", "best practice"],
        "triggers",
        r"^## Tips",
    ),
    # CLI docs
    (
        ["cli", "socket", "bttcli", "command line"],
        "cli",
        r"^## Overview",
    ),
    (
        ["trigger_action", "trigger action", "execute action"],
        "cli",
        r"^### 24\.\s*trigger_action",
    ),
    (
        ["trigger_named", "trigger named", "call named"],
        "cli",
        r"^### 26\.\s*trigger_named",
    ),
    (
        ["add_new_trigger", "add trigger", "create trigger"],
        "cli",
        r"^### 33\.\s*add_new_trigger",
    ),
    (
        ["update_trigger", "update trigger", "modify trigger"],
        "cli",
        r"^### 36\.\s*update_trigger",
    ),
    (
        ["notification", "display_notification"],
        "cli",
        r"^### 6\.\s*display_notification",
    ),
    (
        ["clipboard", "paste"],
        "cli",
        r"^### 2\.\s*get_clipboard_content",
    ),
    (
        ["variable", "set variable", "get variable", "string variable", "number variable"],
        "cli",
        r"^### 12\.\s*set_persistent_string_variable",
    ),
    (
        ["widget", "update widget", "touch bar widget", "stream deck widget"],
        "cli",
        r"^### 40\.\s*refresh_widget",
    ),
    # Variables docs
    (
        ["variable list", "dynamic variable", "available variable", "btt variable"],
        "variables",
        r"^# \[Available Standard Variables\]",
    ),
    (
        ["condition variable", "trigger condition", "activation group"],
        "variables",
        r"^## Advanced Trigger Condition Variables",
    ),
]


def _load_doc(file_key: str) -> str | None:
    """Load a documentation file by key."""
    filename = DOC_FILES.get(file_key)
    if not filename:
        return None
    filepath = DOCS_DIR / filename
    if not filepath.exists():
        return None
    return filepath.read_text(encoding="utf-8")


def _extract_section(content: str, heading_pattern: str) -> str:
    """Extract a section from markdown content starting at the given heading.

    Returns content from the matched heading up to the next heading of equal
    or higher level (fewer #'s), or end of file.
    """
    lines = content.split("\n")
    start_idx = None
    start_level = None

    for i, line in enumerate(lines):
        if start_idx is None:
            if re.match(heading_pattern, line.strip()):
                start_idx = i
                # Determine heading level
                stripped = line.strip()
                start_level = len(stripped) - len(stripped.lstrip("#"))
        else:
            stripped = line.strip()
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                if level <= start_level:
                    return "\n".join(lines[start_idx:i]).strip()

    if start_idx is not None:
        return "\n".join(lines[start_idx:]).strip()

    return ""


def _search_sections(query: str) -> list[tuple[str, str]]:
    """Find matching sections for a query.

    Returns list of (section_heading, content) tuples.
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    results = []
    seen_keys = set()

    # Score each section by keyword match
    scored: list[tuple[int, list[str], str, str]] = []
    for keywords, file_key, heading_pattern in SECTION_INDEX:
        # Exact phrase match in keywords gets highest score
        score = 0
        for kw in keywords:
            if kw in query_lower:
                score += 10
            elif any(w in kw for w in query_words):
                score += 3
            elif any(w in query_lower for w in kw.split()):
                score += 1
        if score > 0:
            scored.append((score, keywords, file_key, heading_pattern))

    scored.sort(key=lambda x: x[0], reverse=True)

    for _score, _kw, file_key, heading_pattern in scored[:3]:
        dedup_key = f"{file_key}:{heading_pattern}"
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        content = _load_doc(file_key)
        if not content:
            continue
        section = _extract_section(content, heading_pattern)
        if section:
            results.append((file_key, section))

    return results


def _list_available_topics() -> str:
    """Return a summary of available documentation topics."""
    return """## Available BTT Reference Topics

Query any of these topics for detailed documentation:

**Trigger Creation:**
- "trigger structure" / "required fields" - Basic trigger JSON format and required fields
- "named trigger" - Named/reusable trigger creation (BTTTriggerType 643)
- "keyboard shortcut" - Keyboard shortcut triggers with key codes and modifiers
- "trackpad" / "gesture" - Trackpad gesture trigger types
- "magic mouse" - Magic Mouse gesture triggers
- "touch bar" - Touch Bar button triggers
- "stream deck" - Stream Deck triggers
- "floating menu" - Floating menu triggers
- "notch bar" - Notch Bar triggers
- "drawing" - Drawing gesture triggers
- "midi" - MIDI triggers
- "siri remote" - Siri Remote triggers
- "key sequence" - Key sequence / typed word triggers
- "example" - Complete trigger JSON examples
- "modifier" - Modifier key codes (Cmd, Opt, Ctrl, Shift)
- "color" / "icon" - Color format and icon configuration
- "tips" - Best practices for trigger JSON

**CLI & Actions:**
- "cli" - CLI/socket overview and command format
- "add trigger" / "create trigger" - add_new_trigger CLI command
- "trigger action" - trigger_action CLI command
- "trigger named" - trigger_named CLI command
- "notification" - display_notification command
- "clipboard" - Clipboard commands
- "variable" - Variable get/set commands
- "widget" - Widget update commands

**Variables:**
- "variable list" / "dynamic variable" - All available BTT variables
- "condition variable" - Advanced trigger condition variables"""


class LookupReferenceInput(BaseModel):
    """Input for looking up BTT reference documentation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    topic: Optional[str] = Field(
        default=None,
        description=(
            "Topic to look up. Examples: 'named trigger', 'keyboard shortcut', "
            "'trigger structure', 'modifier', 'example', 'variable list', "
            "'add trigger', 'trigger action'. "
            "Leave empty to see all available topics."
        ),
    )


@mcp.tool(
    name="btt_lookup_reference",
    annotations={
        "title": "BTT Reference Lookup",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def btt_lookup_reference(params: LookupReferenceInput) -> str:
    """Look up BetterTouchTool reference documentation for trigger types, action IDs,
    JSON formats, variables, and CLI commands.

    IMPORTANT: Call this tool BEFORE creating or updating triggers to get the correct
    JSON format, trigger type IDs, action type IDs, and required fields.

    Examples:
    - Query "named trigger" to get the JSON format for named/reusable triggers
    - Query "keyboard shortcut" to get key codes and modifier flags
    - Query "example" to see complete working trigger JSON examples
    - Query "trigger structure" to get required/optional field reference
    - Query with no topic to see all available documentation topics

    Args:
        params: Contains the topic to look up.

    Returns:
        Relevant BTT documentation section(s).
    """
    if not params.topic:
        return _list_available_topics()

    results = _search_sections(params.topic)

    if not results:
        return (
            f"No documentation found for '{params.topic}'.\n\n"
            + _list_available_topics()
        )

    output_parts = []
    for file_key, section in results:
        source_label = {
            "triggers": "Trigger JSON Reference",
            "cli": "CLI Command Reference",
            "variables": "Variables Reference",
            "actions": "Actions Reference",
        }.get(file_key, file_key)
        output_parts.append(f"**Source: {source_label}**\n\n{section}")

    return "\n\n---\n\n".join(output_parts)
