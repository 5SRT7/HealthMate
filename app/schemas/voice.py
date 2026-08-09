"""Voice API Schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """TTS 请求体。"""

    text: str = Field(
        ..., min_length=1, max_length=2048,
        description="要合成的文本",
        examples=["你好，我是 HealthMate。"],
    )
    voice: str = Field(
        default="zh-CN-XiaoxiaoNeural",
        description="语音名称",
        examples=["zh-CN-XiaoxiaoNeural"],
    )


class ASRResponse(BaseModel):
    """ASR 响应体。"""

    text: str = Field(..., description="转录文本")
    language: str = Field(default="zh", description="检测到的语言")
    duration: float = Field(default=0.0, description="音频时长（秒）")


__all__ = ["TTSRequest", "ASRResponse"]
