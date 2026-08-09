"""SQLAlchemy models for HealthMate."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text, func

from app.database.connection import Base


class UserProfile(Base):
    """用户健康档案。"""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # male / female / other
    height_cm = Column(Integer, nullable=False)
    weight_kg = Column(Integer, nullable=False)
    bmi = Column(Integer, nullable=True)

    # 健康状况
    chronic_conditions = Column(Text, default="[]")  # JSON array
    allergies = Column(Text, default="")
    medications = Column(Text, default="")

    # 生活方式
    diet_type = Column(String(20), default="balanced")  # meat / veggie / balanced
    diet_notes = Column(Text, default="")
    exercise_freq = Column(String(20), default="1-2/week")
    sleep_hours = Column(Integer, nullable=True)
    smoking = Column(String(20), default="never")
    drinking = Column(String(20), default="never")

    # 目标
    health_goals = Column(Text, default="")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DailyArchive(Base):
    """每日对话归档。"""

    __tablename__ = "daily_archives"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    summary = Column(Text, default="")
    key_points = Column(Text, default="[]")  # JSON array
    mood = Column(Text, default="")
    concerns = Column(Text, default="")
    recommendations = Column(Text, default="")
    has_profile_update = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    messages = Column(Text, default="[]")
    bmi = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)  # JSON: [{"role":"user","content":"..."}]
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class KnowledgeCache(Base):
    """知识搜索缓存。"""

    __tablename__ = "knowledge_cache"

    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), index=True)
    query = Column(Text)
    title = Column(Text)
    snippet = Column(Text)
    source_url = Column(Text)
    source_name = Column(Text)
    cached_at = Column(DateTime, server_default=func.now())


__all__ = ["UserProfile", "DailyArchive", "KnowledgeCache"]
