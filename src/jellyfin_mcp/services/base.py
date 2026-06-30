"""Base service classes for jellyfin-mcp."""

import asyncio
import concurrent.futures
import logging
import sys
from abc import ABC, abstractmethod


class ServiceError(Exception):
    """Base service exception."""

    def __init__(self, message: str, code: str = "service_error", details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}


class AuthenticationError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, code="authentication_error")


class JellyfinConnectionError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, code="connection_error")


ConnectionError = JellyfinConnectionError  # backward compat alias


class NotFoundError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, code="not_found")


class BaseService(ABC):
    """Base class for all services."""

    def __init__(self, logger_name: str | None = None):
        self._initialized = False
        self._logger = logging.getLogger(logger_name or self.__class__.__name__)
        if not self._logger.handlers:
            h = logging.StreamHandler(sys.stderr)
            h.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            self._logger.addHandler(h)
            self._logger.setLevel(logging.INFO)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    @property
    def logger(self):
        return self._logger

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run blocking code in thread pool executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    async def initialize(self, **kwargs) -> None:
        if not self._initialized:
            await self._initialize(**kwargs)
            self._initialized = True

    @abstractmethod
    async def _initialize(self, **kwargs) -> None:
        pass

    async def shutdown(self) -> None:
        if self._initialized:
            self._executor.shutdown(wait=False)
            self._initialized = False
