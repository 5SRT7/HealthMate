"""
TTS 模块：使用 edge-tts 进行文本转语音。

返回 MP3 音频流，支持流式播放以降低延迟。
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

import edge_tts

logger = logging.getLogger(__name__)

# 中文语音列表
# zh-CN-XiaoxiaoNeural  女声，温柔
# zh-CN-YunxiNeural     男声，沉稳
# zh-CN-XiaoyiNeural    女声，活泼
# zh-CN-YunjianNeural   男声，科技感
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# edge-tts 支持的所有中文语音
ZH_VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-XiaochenNeural",
    "zh-CN-XiaohanNeural",
    "zh-CN-XiaomengNeural",
    "zh-CN-XiaomoNeural",
    "zh-CN-XiaoqiuNeural",
    "zh-CN-XiaoruiNeural",
    "zh-CN-XiaoshuangNeural",
    "zh-CN-XiaoyanNeural",
    "zh-CN-XiaozhenNeural",
    "zh-CN-YunyangNeural",
    "zh-HK-HiuGaaiNeural",
    "zh-HK-HiuMaanNeural",
    "zh-HK-WanLungNeural",
    "zh-TW-HsiaoChenNeural",
    "zh-TW-HsiaoYuNeural",
    "zh-TW-YunJheNeural",
]


async def stream_tts(
    text: str,
    voice: str = DEFAULT_VOICE,
) -> AsyncGenerator[bytes, None]:
    """流式生成 TTS 音频。

    以 MP3 块的形式逐块生成，可实现边生成边播放。

    Args:
        text:  要朗读的文本
        voice: 语音名称

    Yields:
        MP3 音频字节块
    """
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


async def generate_tts(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """一次性生成完整 TTS 音频。"""
    communicate = edge_tts.Communicate(text, voice)
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


__all__ = ["stream_tts", "generate_tts", "DEFAULT_VOICE", "ZH_VOICES"]
