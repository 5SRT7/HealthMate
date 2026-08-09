"""Profile API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    """创建/更新健康档案的请求体。"""
    age: int = Field(..., ge=1, le=150, description="年龄")
    gender: str = Field(..., description="性别: male/female/other")
    height_cm: int = Field(..., ge=50, le=250, description="身高(cm)")
    weight_kg: int = Field(..., ge=10, le=500, description="体重(kg)")
    chronic_conditions: list[str] = Field(default=[], description="慢性病列表")
    allergies: str = Field(default="", description="过敏史")
    medications: str = Field(default="", description="用药情况")
    diet_type: str = Field(default="balanced", description="饮食类型: meat/veggie/balanced")
    diet_notes: str = Field(default="", description="饮食备注")
    exercise_freq: str = Field(default="1-2/week", description="运动频率")
    sleep_hours: int | None = Field(default=None, ge=0, le=24, description="平均睡眠(小时)")
    smoking: str = Field(default="never", description="吸烟: never/quit/occasional/daily")
    drinking: str = Field(default="never", description="饮酒: never/occasional/regular")
    health_goals: str = Field(default="", description="健康目标")


class ProfileResponse(BaseModel):
    """健康档案响应体。"""
    age: int
    gender: str
    height_cm: int
    weight_kg: int
    bmi: float | None = None
    chronic_conditions: list[str] = []
    allergies: str = ""
    medications: str = ""
    diet_type: str = "balanced"
    diet_notes: str = ""
    exercise_freq: str = "1-2/week"
    sleep_hours: int | None = None
    smoking: str = "never"
    drinking: str = "never"
    health_goals: str = ""
    updated_at: str | None = None


class ProfileCheckResponse(BaseModel):
    """用于前端判断是否首次使用。"""
    exists: bool


__all__ = ["ProfileCreate", "ProfileResponse", "ProfileCheckResponse"]
