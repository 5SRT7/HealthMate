"""Archive API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.database.crud import get_archive_detail, search_archives
from app.schemas.archive import ArchiveDetail, ArchiveListResponse, ArchiveListItem

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/archives",
    response_model=ArchiveListResponse,
    summary="搜索归档",
)
async def list_archives(
    q: str = Query(default="", description="关键词搜索"),
    year: int | None = Query(default=None, ge=2020, le=2099),
    month: int | None = Query(default=None, ge=1, le=12),
) -> ArchiveListResponse:
    """搜索每日归档记录。支持关键词和年月筛选。"""
    archives = search_archives(keyword=q, year=year, month=month)
    items = [
        ArchiveListItem(
            date=a["date"],
            summary=a["summary"][:200],
            message_count=a["message_count"],
        )
        for a in archives
    ]
    logger.info("GET /archives: q=%s year=%s month=%s -> %d results", q, year, month, len(items))
    return ArchiveListResponse(archives=items)




@router.delete(
    "/archives/{date}",
    summary="删除归档",
)
async def delete_archive_route(date: str) -> dict:
    """删除某天的归档记录。"""
    from app.database.crud import delete_archive as _delete
    deleted = _delete(date)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 {date} 的归档",
        )
    logger.info("Archive deleted: %s", date)
    return {"status": "deleted"}

@router.get(
    "/archives/{date}",
    response_model=ArchiveDetail,
    summary="归档详情",
)
async def get_archive(date: str) -> ArchiveDetail:
    """获取某天的完整归档，含对话消息。"""
    detail = get_archive_detail(date)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 {date} 的归档",
        )
    return ArchiveDetail(
        date=detail["date"],
        summary=detail.get("summary", ""),
        key_points=detail.get("key_points", []),
        mood=detail.get("mood", ""),
        concerns=detail.get("concerns", ""),
        recommendations=detail.get("recommendations", ""),
        message_count=detail.get("message_count", 0),
        messages=[{"role": m["role"], "content": m["content"]} for m in detail.get("messages", [])],
    )


__all__ = ["router"]
