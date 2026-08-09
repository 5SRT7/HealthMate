"""Profile API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.database.crud import (
    delete_profile as _delete_profile,
    get_profile,
    profile_exists,
    upsert_profile,
)
from app.schemas.profile import (
    ProfileCheckResponse,
    ProfileCreate,
    ProfileResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/profile/check",
    response_model=ProfileCheckResponse,
    summary="检查档案是否存在",
)
async def check_profile() -> ProfileCheckResponse:
    """判断用户是否已填写健康档案。"""
    return ProfileCheckResponse(exists=profile_exists())


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="获取健康档案",
)
async def read_profile() -> ProfileResponse:
    """获取当前用户的健康档案。"""
    p = get_profile()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请先创建健康档案",
        )
    return ProfileResponse(**p)


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="创建/更新健康档案",
)
async def update_profile(data: ProfileCreate) -> ProfileResponse:
    """创建或更新健康档案。"""
    result = upsert_profile(data.model_dump())
    logger.info(
        "Profile updated: age=%s, height=%s, weight=%s",
        data.age, data.height_cm, data.weight_kg,
    )
    return ProfileResponse(**result)


@router.delete(
    "/profile",
    summary="删除健康档案",
)
async def delete_profile() -> dict:
    """删除当前用户的健康档案。"""
    deleted = _delete_profile()
    if deleted:
        logger.info("Profile deleted")
        return {"status": "deleted"}
    return {"status": "not_found"}


__all__ = ["router"]
