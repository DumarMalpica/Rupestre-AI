from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Generator


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class _MockTracer:
    @contextmanager
    def trace(self, *args, **kwargs) -> Generator[None, None, None]:
        yield

    @contextmanager
    def span(self, *args, **kwargs) -> Generator[None, None, None]:
        yield


def get_tracer():
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")

    if public_key and secret_key:
        from langfuse import Langfuse

        return Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )

    return _MockTracer()
