"""CRUD operations for all models.

All functions are synchronous. LangGraph nodes run in threads,
so this is safe to call from agent code.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any

from app.database.connection import get_session
from app.database.models import DailyArchive, KnowledgeCache, UserProfile


# ═══════════════════════════════════════════════════════════════
# Profile
# ═══════════════════════════════════════════════════════════════

def _compute_bmi(height_cm: int, weight_kg: int) -> int:
    """BMI = weight(kg) / height(m)²"""
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def get_profile() -> dict[str, Any] | None:
    """Get the current user profile. Returns dict or None."""
    with get_session() as session:
        p = session.query(UserProfile).order_by(UserProfile.id.desc()).first()
        if not p:
            return None
        return _profile_to_dict(p)


def _profile_to_dict(p: UserProfile) -> dict[str, Any]:
    return {
        "id": p.id,
        "age": p.age,
        "gender": p.gender,
        "height_cm": p.height_cm,
        "weight_kg": p.weight_kg,
        "bmi": p.bmi,
        "chronic_conditions": json.loads(p.chronic_conditions) if p.chronic_conditions else [],
        "allergies": p.allergies or "",
        "medications": p.medications or "",
        "diet_type": p.diet_type or "balanced",
        "diet_notes": p.diet_notes or "",
        "exercise_freq": p.exercise_freq or "1-2/week",
        "sleep_hours": p.sleep_hours,
        "smoking": p.smoking or "never",
        "drinking": p.drinking or "never",
        "health_goals": p.health_goals or "",
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def upsert_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Create or update the user profile. Auto-computes BMI."""
    # Serialize list fields to JSON for SQLite TEXT columns
    if isinstance(data.get("chronic_conditions"), list):
        data["chronic_conditions"] = json.dumps(data["chronic_conditions"], ensure_ascii=False)
    with get_session() as session:
        profile = session.query(UserProfile).order_by(UserProfile.id.desc()).first()

        # Compute BMI from height/weight
        h = data.get("height_cm") or (profile.height_cm if profile else None)
        w = data.get("weight_kg") or (profile.weight_kg if profile else None)
        if "bmi" not in data and h and w:
            data["bmi"] = _compute_bmi(int(h), int(w))

        if profile:
            for k, v in data.items():
                if k not in ("id", "created_at", "updated_at"):
                    setattr(profile, k, v)
        else:
            profile = UserProfile(**data)
            session.add(profile)

        session.commit()
        session.refresh(profile)
        return _profile_to_dict(profile)



def delete_profile() -> bool:
    """Delete the current user profile."""
    from app.database.models import UserProfile
    with get_session() as session:
        profile = session.query(UserProfile).order_by(UserProfile.id.desc()).first()
        if profile:
            session.delete(profile)
            session.commit()
            return True
        return False


def profile_exists() -> bool:
    """Check if a profile has been created."""
    with get_session() as session:
        return session.query(UserProfile).count() > 0


# ═══════════════════════════════════════════════════════════════
# Daily Archive
# ═══════════════════════════════════════════════════════════════

def get_archive(for_date: date | None = None) -> dict[str, Any] | None:
    """Get archive for a specific date. Defaults to today."""
    if for_date is None:
        for_date = date.today()
    with get_session() as session:
        a = session.query(DailyArchive).filter(
            DailyArchive.date == for_date
        ).first()
        if not a:
            return None
        return _archive_to_dict(a)


def get_recent_archives(days: int = 7) -> list[dict[str, Any]]:
    """Get archives from the last N days."""
    from datetime import timedelta

    since = date.today() - timedelta(days=days)
    with get_session() as session:
        rows = (
            session.query(DailyArchive)
            .filter(DailyArchive.date >= since)
            .order_by(DailyArchive.date.desc())
            .all()
        )
        return [_archive_to_dict(a) for a in rows]


def upsert_archive(data: dict[str, Any]) -> dict[str, Any]:
    """Create or update today's archive."""
    with get_session() as session:
        archive = session.query(DailyArchive).filter(
            DailyArchive.date == date.today()
        ).first()

        if archive:
            for k, v in data.items():
                if k not in ("id", "date", "created_at", "updated_at"):
                    setattr(archive, k, v)
        else:
            data.setdefault("date", date.today())
            archive = DailyArchive(**data)
            session.add(archive)

        # Snapshot current BMI/weight from profile
        profile = get_profile()
        if profile:
            archive.bmi = profile.get("bmi")
            archive.weight_kg = profile.get("weight_kg")
        session.commit()
        session.refresh(archive)
        return _archive_to_dict(archive)






def delete_archive(for_date: str) -> bool:
    """删除某天的归档记录。"""
    from datetime import date
    try:
        d = date.fromisoformat(for_date)
    except ValueError:
        return False
    with get_session() as session:
        a = session.query(DailyArchive).filter(DailyArchive.date == d).first()
        if a:
            session.delete(a)
            session.commit()
            return True
        return False


def search_archives(
    keyword: str = "",
    year: int | None = None,
    month: int | None = None,
    limit: int = 100,
) -> list[dict]:
    """搜索归档记录。支持关键词搜索和年月筛选。"""
    from datetime import date
    with get_session() as session:
        q = session.query(DailyArchive)

        # 按年月筛选
        if year and month:
            start = date(year, month, 1)
            end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            q = q.filter(DailyArchive.date >= start, DailyArchive.date < end)

        # 关键词搜索（summary / messages / key_points）
        if keyword.strip():
            kw = f"%{keyword.strip()}%"
            q = q.filter(
                DailyArchive.summary.ilike(kw) |
                DailyArchive.messages.ilike(kw) |
                DailyArchive.key_points.ilike(kw)
            )

        rows = q.order_by(DailyArchive.date.desc()).limit(limit).all()
        return [_archive_to_dict(r) for r in rows]


def get_archive_detail(for_date: str) -> dict | None:
    """获取某天的完整归档，包含对话消息。"""
    from datetime import date
    try:
        d = date.fromisoformat(for_date)
    except ValueError:
        return None
    with get_session() as session:
        a = session.query(DailyArchive).filter(DailyArchive.date == d).first()
        if not a:
            return None
        result = _archive_to_dict(a)
        result["messages"] = json.loads(a.messages) if a.messages else []
        return result


def _archive_to_dict(a: DailyArchive) -> dict[str, Any]:
    return {
        "id": a.id,
        "date": a.date.isoformat() if a.date else None,
        "summary": a.summary or "",
        "key_points": json.loads(a.key_points) if a.key_points else [],
        "mood": a.mood or "",
        "concerns": a.concerns or "",
        "recommendations": a.recommendations or "",
        "has_profile_update": a.has_profile_update or False,
        "message_count": a.message_count or 0,
        "bmi": a.bmi,
        "weight_kg": a.weight_kg,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# ═══════════════════════════════════════════════════════════════
# Knowledge Cache
# ═══════════════════════════════════════════════════════════════

def _hash_query(q: str) -> str:
    return hashlib.sha256(q.encode()).hexdigest()[:16]


def get_cached(query: str) -> list[dict[str, Any]] | None:
    """Return cached results for a query, or None."""
    qh = _hash_query(query)
    with get_session() as session:
        rows = (
            session.query(KnowledgeCache)
            .filter(KnowledgeCache.query_hash == qh)
            .all()
        )
        if rows:
            return [
                {
                    "title": r.title,
                    "snippet": r.snippet,
                    "source_url": r.source_url,
                    "source_name": r.source_name,
                }
                for r in rows
            ]
        return None


def cache_results(query: str, results: list[dict[str, str]]) -> None:
    """Cache search results for a query."""
    qh = _hash_query(query)
    with get_session() as session:
        for r in results:
            entry = KnowledgeCache(
                query_hash=qh,
                query=query,
                title=r.get("title", ""),
                snippet=r.get("snippet", ""),
                source_url=r.get("source_url", ""),
                source_name=r.get("source_name", ""),
            )
            session.add(entry)
        session.commit()


__all__ = [
    "get_profile", "upsert_profile", "profile_exists",
    "get_archive", "get_recent_archives", "upsert_archive",
    "get_cached", "cache_results",
]
