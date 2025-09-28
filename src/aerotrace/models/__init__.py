"""
AeroTrace Data Models

Core data structures for aviation engine monitoring system telemetry.
"""

from .engine import EngineData, CylinderReading, CylinderReadings

__all__ = [
    "EngineData",
    "CylinderReading",
    "CylinderReadings",
]