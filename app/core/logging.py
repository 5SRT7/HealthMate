"""
统一日志配置。

集中管理日志格式和级别，避免各模块各自配置。
"""

from __future__ import annotations

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """配置全局日志。

    格式：时间 | 级别 | 模块名 | 消息
    级别从 settings.LOG_LEVEL 读取，默认 INFO。
    
    调用一次即可（通常在 main.py 入口处）。
    """
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # 清除已有 handler 避免重复添加
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # 减少第三方库的噪音
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取命名 logger，推荐在模块级调用。

    Usage:
        logger = get_logger(__name__)
        logger.info("...")
    """
    return logging.getLogger(name)


__all__ = ["setup_logging", "get_logger"]
