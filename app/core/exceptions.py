"""
统一异常定义。

所有业务异常从 AppException 继承，便于 API 层统一捕获处理。
"""

from __future__ import annotations


class AppException(Exception):
    """应用基础异常。"""

    def __init__(self, message: str, code: str = "UNKNOWN") -> None:
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")


class LLMException(AppException):
    """LLM 调用相关异常。"""

    def __init__(self, message: str, code: str = "LLM_ERROR") -> None:
        super().__init__(message=message, code=code)


class ConfigException(AppException):
    """配置相关异常。"""

    def __init__(self, message: str, code: str = "CONFIG_ERROR") -> None:
        super().__init__(message=message, code=code)


class AgentException(AppException):
    """Agent 执行相关异常。"""

    def __init__(self, message: str, code: str = "AGENT_ERROR") -> None:
        super().__init__(message=message, code=code)


__all__ = ["AppException", "LLMException", "ConfigException", "AgentException"]
