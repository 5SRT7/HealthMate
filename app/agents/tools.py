"""
LangChain tools used by the Data Analyzer supervisor.

Each tool is a @tool-decorated function that the LLM can call.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from duckduckgo_search import DDGS
from langchain_core.tools import tool

from app.database.crud import (
    cache_results,
    get_cached,
    get_profile,
    get_recent_archives,
    profile_exists,
    upsert_profile,
)

logger = logging.getLogger(__name__)


@tool
def read_user_profile() -> str:
    """读取当前用户的健康档案。每次对话时先调用此工具获取用户的基本健康信息。

    Returns:
        用户的健康档案文本，或提示用户尚未填写档案。
    """
    p = get_profile()
    if not p:
        return "用户尚未填写健康档案。请引导用户填写基本信息（年龄、性别、身高、体重等）。"
    return json.dumps(p, ensure_ascii=False, indent=2)


@tool
def update_user_profile_field(field: str, value: str) -> str:
    """更新用户健康档案中的某个字段。当用户提到身体状况变化时调用。

    可更新的字段: age, gender, height_cm, weight_kg, allergies, medications,
    diet_type, diet_notes, exercise_freq, sleep_hours, smoking, drinking, health_goals,
    chronic_conditions（多个条件用逗号分隔）

    Args:
        field: 字段名
        value: 字段的字符串值（数字字段会自动转换）

    Returns:
        更新结果
    """
    profile = get_profile()
    if not profile:
        return "用户尚未创建档案，请先用界面引导填写。"

    # 转换值类型
    converted: Any = value
    if field in ("age", "height_cm", "weight_kg", "sleep_hours"):
        converted = int(value)
    if field == "chronic_conditions":
        converted = [c.strip() for c in value.split(",")]

    try:
        upsert_profile({field: converted})
        logger.info("Profile field updated via agent: %s = %s", field, value)
        return f"已更新 {field} 为 {value}"
    except Exception as exc:
        logger.exception("Failed to update profile field")
        return f"更新失败: {exc}"


@tool
def search_health_knowledge(query: str) -> str:
    """搜索权威健康知识和参考资料。当需要引用公开的健康指南或建议时调用。

    搜索来源包括但不限于：《中国居民膳食指南》、WHO 健康建议、PubMed 等。
    结果会自动缓存，相同问题不会重复搜索。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果（标题、摘要、来源URL）
    """
    # 检查缓存
    cached = get_cached(query)
    if cached:
        results = _format_results(cached)
        logger.info("Knowledge cache hit for: %s", query[:40])
        return f"[缓存结果]\n{results}"

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=5))
    except Exception as exc:
        logger.warning("DuckDuckGo search failed: %s", exc)
        return f"搜索暂时不可用: {exc}"

    results = []
    cache_entries = []
    for r in raw:
        entry = {
            "title": r.get("title", ""),
            "snippet": r.get("body", ""),
            "source_url": r.get("href", ""),
            "source_name": _extract_source(r.get("href", "")),
        }
        results.append(entry)
        cache_entries.append(entry)

    # 缓存结果
    try:
        cache_results(query, cache_entries)
    except Exception as exc:
        logger.warning("Failed to cache results: %s", exc)

    return _format_results(results)


@tool
def read_recent_archives(days: int = 7) -> str:
    """读取最近几天的健康归档记录，了解用户的近期状况变化。

    Args:
        days: 回溯天数，默认7天

    Returns:
        近期归档摘要
    """
    archives = get_recent_archives(days)
    if not archives:
        return f"近 {days} 天没有归档记录。"

    lines = [f"近 {days} 天的健康归档（共 {len(archives)} 天）："]
    for a in archives:
        lines.append(f"\n--- {a['date']} ---")
        lines.append(f"摘要: {a['summary'][:100]}")
        if a["key_points"]:
            lines.append(f"要点: {'; '.join(a['key_points'][:3])}")
        if a["mood"]:
            lines.append(f"情绪: {a['mood']}")
        lines.append(f"消息数: {a['message_count']}")

    return "\n".join(lines)


# ── 辅助函数 ──────────────────────────────────────────────────────

def _format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        lines.append(f"   {r['snippet'][:200]}")
        lines.append(f"   来源: {r['source_url']}")
        lines.append("")
    return "\n".join(lines) if lines else "未找到相关结果。"


def _extract_source(url: str) -> str:
    """从 URL 中提取网站名称。"""
    import re
    match = re.search(r"https?://([^/]+)", url)
    if match:
        domain = match.group(1)
        return domain.replace("www.", "")
    return url


# 导出所有工具列表供 LangGraph 使用
HEALTH_TOOLS = [
    read_user_profile,
    update_user_profile_field,
    search_health_knowledge,
    read_recent_archives,
]

__all__ = ["HEALTH_TOOLS"]

# 让 DB 工具在数据库未初始化时不崩溃
import functools

def _db_safe(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "no such table" in str(e).lower() or "no such table" in str(e).lower():
                logger.warning("DB not ready, skipping tool: %s", func.__name__)
                return "（数据库暂不可用）"
            raise
    return wrapper
