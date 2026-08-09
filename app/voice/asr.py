"""
ASR 模块：使用 faster-whisper 进行语音识别。

模型懒加载（首次调用时下载 base 模型），后续复用。
转录结果自动转换为简体中文。
"""

from __future__ import annotations

import logging
import os
import tempfile

from zhconv import convert as zh_convert

from app.core.exceptions import LLMException

logger = logging.getLogger(__name__)

_ASR_MODEL = None  # type: ignore


def get_asr_model():
    """懒加载 faster-whisper base 模型（int8 量化，CPU）。"""
    global _ASR_MODEL
    if _ASR_MODEL is None:
        logger.info("Loading faster-whisper base model (from cache or downloading)...")
        from faster_whisper import WhisperModel

        _ASR_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("ASR model loaded")
    return _ASR_MODEL


def transcribe(
    audio_bytes: bytes,
    language: str | None = "zh",
    beam_size: int = 5,
) -> dict:
    """将音频字节转录为简体中文文本。

    Args:
        audio_bytes: 音频数据（ffmpeg 支持即可）
        language:   语言代码，None 为自动检测
        beam_size:  搜索宽度，越大越准但越慢

    Returns:
        {"text": "简体文本", "language": "zh", "duration": 2.5}
    """
    model = get_asr_model()

    suffix = ".webm"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        tmp.write(audio_bytes)
        tmp.close()
        tmp_path = tmp.name

        logger.info("Transcribing %d bytes (lang=%s)...", len(audio_bytes), language)
        segments, info = model.transcribe(
            tmp_path,
            language=language,
            beam_size=beam_size,
        )
        raw_text = "".join(seg.text for seg in segments).strip()

        # 繁体 → 简体
        simplified = zh_convert(raw_text, "zh-cn")
        logger.info(
            "ASR: %s (lang=%s, dur=%.1fs, simp=%s)",
            simplified[:60], info.language, info.duration,
            raw_text != simplified,
        )

        return {
            "text": simplified,
            "language": info.language,
            "duration": info.duration,
        }
    except Exception as exc:
        logger.exception("ASR failed")
        raise LLMException(f"语音识别失败: {exc}") from exc
    finally:
        os.unlink(tmp_path)


__all__ = ["transcribe"]
