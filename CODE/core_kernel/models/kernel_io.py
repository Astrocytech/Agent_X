"""Kernel I/O — re-exports canonical contracts from kernel_contracts.py.

Maintains backward-compatible import path ``core_kernel.kernel_io``.
New code should import directly from ``core_kernel.contracts.kernel_contracts``.
"""

from __future__ import annotations

from core_kernel.contracts.kernel_contracts import KernelInput, KernelOutput  # noqa: F401

__all__ = [
    "KernelInput",
    "KernelOutput",
]
