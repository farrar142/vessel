"""
Vessel Utilities Module
"""

from vessel.utils.async_support import (
    is_async_callable,
    run_sync_or_async,
)

__all__ = [
    "is_async_callable",
    "run_sync_or_async",
]
