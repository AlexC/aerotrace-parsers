"""
Data models for standardized EMS telemetry representation
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Cylinder:
    """Temperature reading for a specific cylinder (EGT or CHT)"""

    number: int  # Cylinder number (1-based)
    value: float  # Temperature in degrees Fahrenheit

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError("Cylinder number must be >= 1")
        if not isinstance(self.value, (int, float)):
            raise ValueError("Temperature value must be numeric")


class Cylinders:
    """Collection of cylinder temperature readings with utility methods"""

    def __init__(self, readings: List[Cylinder]) -> None:
        self._readings = readings

    def __iter__(self):
        return iter(self._readings)

    def __len__(self) -> int:
        return len(self._readings)

    def __getitem__(self, index):
        return self._readings[index]

    def get_hottest(self) -> Optional[Cylinder]:
        """Get the cylinder with the highest temperature reading"""
        if not self._readings:
            return None

        return max(self._readings, key=lambda x: x.value)

    def get_coolest(self) -> Optional[Cylinder]:
        """Get the cylinder with the lowest temperature reading"""
        if not self._readings:
            return None

        return min(self._readings, key=lambda x: x.value)

    def get_difference(self) -> Optional[float]:
        """Get the temperature difference between hottest and coolest cylinders"""
        hottest = self.get_hottest()
        coolest = self.get_coolest()

        if hottest and coolest:
            return hottest.value - coolest.value

        return None


@dataclass
class RPM:
    """Engine RPM data with dual magneto support"""

    left: Optional[int] = None
    right: Optional[int] = None
    computed: Optional[int] = None

    @property
    def difference(self) -> Optional[int]:
        """Calculate RPM difference between magnetos (useful for detecting mag issues)"""
        if self.left is not None and self.right is not None:
            return abs(self.left - self.right)
        return None


@dataclass
class Fuel:
    """Fuel system data with pressure, flow, quantity and alerts"""

    pressure: Optional[float] = None  # PSI
    flow: Optional[float] = None  # LPH
    quantity: Optional[float] = None  # L
    pressure_alert: bool = False
    quantity_alert: bool = False

    @property
    def has_active_alert(self) -> bool:
        """Check if any fuel system alerts are active"""
        return self.pressure_alert or self.quantity_alert


@dataclass
class Oil:
    """Oil system data with pressure, temperature and alerts"""

    pressure: Optional[float] = None  # PSI
    temperature: Optional[float] = None  # Fahrenheit
    pressure_alert: bool = False
    temperature_alert: bool = False

    @property
    def has_active_alert(self) -> bool:
        """Check if any oil system alerts are active"""
        return self.pressure_alert or self.temperature_alert


@dataclass
class Electrical:
    """Electrical system data"""

    volts: Optional[float] = None  # V
    amps: Optional[float] = None  # A


@dataclass
class EngineData:
    """Standardized engine data format for all EMS types"""

    rpm: RPM = field(default_factory=RPM)
    manifold_pressure: Optional[float] = None  # InHg

    # Cylinder temperatures
    egts: Cylinders = field(default_factory=lambda: Cylinders([]))
    chts: Cylinders = field(default_factory=lambda: Cylinders([]))

    # System components
    fuel: Fuel = field(default_factory=Fuel)
    oil: Oil = field(default_factory=Oil)
    electrical: Electrical = field(default_factory=Electrical)

    # General
    g_force: Optional[float] = None
