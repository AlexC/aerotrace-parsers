"""
Data models for standardized EMS telemetry representation.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CylinderReading:
    """
    Temperature reading for a specific cylinder (EGT or CHT).

    Args:
        number: Cylinder number (1-based)
        value: Temperature in degrees Fahrenheit
    """
    number: int
    value: float

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError("Cylinder number must be >= 1")
        if not isinstance(self.value, (int, float)):
            raise ValueError("Temperature value must be numeric")


class CylinderReadings:
    """
    Collection of cylinder temperature readings with utility methods.
    """

    def __init__(self, readings: List[CylinderReading]) -> None:
        self._readings = readings

    def __iter__(self):
        return iter(self._readings)

    def __len__(self) -> int:
        return len(self._readings)

    def __getitem__(self, index):
        return self._readings[index]

    def get_hottest(self) -> Optional[CylinderReading]:
        """Get the cylinder with the highest temperature reading."""
        if not self._readings:
            return None

        return max(self._readings, key=lambda x: x.value)

    def get_coolest(self) -> Optional[CylinderReading]:
        """Get the cylinder with the lowest temperature reading."""
        if not self._readings:
            return None

        return min(self._readings, key=lambda x: x.value)

    def get_difference(self) -> Optional[float]:
        """Get the temperature difference between hottest and coolest cylinders."""
        hottest = self.get_hottest()
        coolest = self.get_coolest()

        if hottest and coolest:
            return hottest.value - coolest.value

        return None


@dataclass
class EngineData:
    """
    Standardized engine data format for all EMS types

    All temperature values are in Fahrenheit, pressure in PSI, electrical
    values in standard units (Volts, Amps), and G-force as a multiplier
    """
    rpm: Optional[float] = None
    manifold_pressure: Optional[float] = None  # InHg

    # Cylinders
    egts: CylinderReadings = field(default_factory=lambda: CylinderReadings([]))
    chts: CylinderReadings = field(default_factory=lambda: CylinderReadings([]))

    # Oil system
    oil_pressure: Optional[float] = None  # PSI
    oil_temperature: Optional[float] = None  # °F

    # Fuel system
    fuel_pressure: Optional[float] = None  # PSI

    # Electrical system
    volts: Optional[float] = None  # V
    amps: Optional[float] = None  # A

    # General
    g_force: Optional[float] = None  # G multiplier
