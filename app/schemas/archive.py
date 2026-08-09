"""Archive API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArchiveMessage(BaseModel):
    """单条对话消息。"""
    role: str = Field(..., description="user / assistant")
    content: str = Field(..., description="消息内容")


class ArchiveListItem(BaseModel):
    """归档列表项。"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    summary: str = Field(default="", description="摘要")
    message_count: int = Field(default=0, description="消息数")


class ArchiveListResponse(BaseModel):
    """归档列表响应。"""
    archives: list[ArchiveListItem] = Field(default=[], description="归档列表")


class ArchiveDetail(BaseModel):
    """归档详情（含完整对话）。"""
    date: str = Field(..., description="日期")
    summary: str = Field(default="", description="摘要")
    key_points: list[str] = Field(default=[], description="关键信息")
    mood: str = Field(default="", description="情绪")
    concerns: str = Field(default="", description="顾虑")
    recommendations: str = Field(default="", description="建议")
    message_count: int = Field(default=0)
    messages: list[ArchiveMessage] = Field(default=[], description="完整对话")


__all__ = ["ArchiveListItem", "ArchiveListResponse", "ArchiveDetail", "ArchiveMessage"]
