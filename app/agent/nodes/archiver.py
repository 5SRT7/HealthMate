"""
Memory Agent (archiver): post-conversation archiving.

Saves daily summaries and full conversation messages.
"""

from __future__ import annotations

import json
import logging

from app.agent.state import AgentState
from app.database.crud import get_archive, upsert_archive

logger = logging.getLogger(__name__)


def _serialize_messages(messages: list) -> list[dict]:
    """Convert LangChain messages to simple JSON format for storage."""
    result: list[dict] = []
    for m in messages:
        if getattr(m, "tool_calls", None):
            continue
        if getattr(m, "type", "") == "system":
            continue
        role = "user" if getattr(m, "type", "") == "human" else "assistant"
        content = str(m.content) if m.content else ""
        if content:
            result.append({"role": role, "content": content})
    return result


def archiver_node(state: AgentState) -> dict:
    """Archive today's conversation. Saves messages and summary."""
    try:
        raw_messages = state.get("messages", [])
        if len(raw_messages) < 2:
            logger.info("Archiver: skipping (too few messages)")
            return {}

        serialized = _serialize_messages(raw_messages)
        if not serialized:
            return {}

        # Last assistant response as summary
        last_ai = [m for m in serialized if m["role"] == "assistant"]
        summary = last_ai[-1]["content"][:300] if last_ai else ""

        # Merge with existing today's archive
        existing = get_archive()
        existing_msgs: list[dict] = existing.get("messages", []) if existing else []

        # Keep the existing messages up to the point before new ones
        merged = serialized

        upsert_archive({
            "summary": summary or (existing and existing.get("summary", "")),
            "message_count": len(serialized),
            "messages": json.dumps(merged, ensure_ascii=False),
        })

        logger.info("Archived %d messages for today", len(serialized))
    except Exception as exc:
        logger.warning("Archive skipped (non-fatal): %s", exc)
    return {}


__all__ = ["archiver_node"]
