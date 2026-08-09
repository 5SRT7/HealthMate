"""
Voice API 路由。

提供：
- POST /asr   语音识别（音频 → 文本）
- POST /tts   语音合成（文本 → 流式音频）
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.voice import ASRResponse, TTSRequest
from app.voice.asr import transcribe
from app.voice.tts import stream_tts

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/asr",
    response_model=ASRResponse,
    summary="语音识别",
    description="上传音频文件，返回转录文本。",
)
async def asr_endpoint(
    audio: UploadFile = File(...),
) -> ASRResponse:
    """语音识别端点。

    接收音频文件，使用 faster-whisper base 模型转录。
    支持 WAV / WebM / MP3 等格式。
    """
    logger.info("POST /asr: file=%s size=?", audio.filename)

    audio_bytes = await audio.read()
    result = transcribe(audio_bytes)

    return ASRResponse(
        text=result["text"],
        language=result["language"],
        duration=result["duration"],
    )


@router.post(
    "/tts",
    summary="语音合成",
    description="将文本合成为 MP3 音频，流式返回。",
    response_class=StreamingResponse,
)
async def tts_endpoint(request: TTSRequest) -> StreamingResponse:
    """语音合成端点。

    使用 edge-tts 将文本合成为 MP3 音频。
    以流式方式返回，前端边接收边播放。
    """
    logger.info(
        "POST /tts: text=%s ... voice=%s",
        request.text[:40],
        request.voice,
    )

    return StreamingResponse(
        stream_tts(request.text, request.voice),
        media_type="audio/mpeg",
        headers={
            "X-Voice": request.voice,
            "X-Text-Length": str(len(request.text)),
        },
    )


__all__ = ["router"]
