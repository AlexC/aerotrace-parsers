"""
Tests for aerotrace.models.engine module.
"""

import pytest
from aerotrace.models import Cylinder, Cylinders, RPM, Fuel, Oil, Electrical


class TestCylinder:
    """Test cases for the CylinderReading dataclass."""

    def test_valid_cylinder_reading(self):
        """Test creating a valid cylinder reading."""
        reading = Cylinder(number=1, value=1200.5)
        assert reading.number == 1
        assert reading.value == 1200.5

    def test_cylinder_number_validation(self):
        """Test validation of cylinder number."""
        Cylinder(number=1, value=1200.0)
        Cylinder(number=6, value=1200.0)

        with pytest.raises(ValueError, match="Cylinder number must be >= 1"):
            Cylinder(number=0, value=1200.0)

        with pytest.raises(ValueError, match="Cylinder number must be >= 1"):
            Cylinder(number=-1, value=1200.0)

    def test_temperature_value_validation(self):
        """Test validation of temperature values."""
        Cylinder(number=1, value=1200)
        Cylinder(number=1, value=1200.5)
        Cylinder(number=1, value=0.0)
        Cylinder(number=1, value=-10.5)

        with pytest.raises(ValueError, match="Temperature value must be numeric"):
            Cylinder(number=1, value="1200")  # type: ignore

        with pytest.raises(ValueError, match="Temperature value must be numeric"):
            Cylinder(number=1, value=None)  # type: ignore


class TestCylinders:
    """Test cases for the Cylinders collection class."""

    def test_empty_readings(self):
        """Test behavior with empty readings list."""
        readings = Cylinders([])
        assert len(readings) == 0
        assert list(readings) == []
        assert readings.get_hottest() is None
        assert readings.get_coolest() is None
        assert readings.get_difference() is None

    def test_single_reading(self):
        """Test behavior with a single reading."""
        reading = Cylinder(number=1, value=1200.0)
        readings = Cylinders([reading])

        assert len(readings) == 1
        assert list(readings) == [reading]
        assert readings[0] == reading
        assert readings.get_hottest() == reading
        assert readings.get_coolest() == reading
        assert readings.get_difference() == 0.0

    def test_multiple_readings(self):
        """Test behavior with multiple readings."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1250.5)
        reading3 = Cylinder(number=3, value=1180.0)
        readings = Cylinders([reading1, reading2, reading3])

        assert len(readings) == 3
        assert list(readings) == [reading1, reading2, reading3]
        assert readings[1] == reading2

    def test_get_hottest(self):
        """Test finding the hottest cylinder."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1250.5)
        reading3 = Cylinder(number=3, value=1180.0)
        readings = Cylinders([reading1, reading2, reading3])

        hottest = readings.get_hottest()
        assert hottest is not None
        assert hottest.number == 2
        assert hottest.value == 1250.5

    def test_get_coolest(self):
        """Test finding the coolest cylinder."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1250.5)
        reading3 = Cylinder(number=3, value=1180.0)
        readings = Cylinders([reading1, reading2, reading3])

        coolest = readings.get_coolest()
        assert coolest is not None
        assert coolest.number == 3
        assert coolest.value == 1180.0

    def test_get_difference(self):
        """Test calculating temperature difference."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1250.5)
        reading3 = Cylinder(number=3, value=1180.0)
        readings = Cylinders([reading1, reading2, reading3])

        difference = readings.get_difference()
        assert difference == 70.5

    def test_identical_temperatures(self):
        """Test behavior when all temperatures are identical."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1200.0)
        reading3 = Cylinder(number=3, value=1200.0)
        readings = Cylinders([reading1, reading2, reading3])

        hottest = readings.get_hottest()
        coolest = readings.get_coolest()
        assert hottest is not None
        assert coolest is not None
        assert hottest.value == 1200.0
        assert coolest.value == 1200.0
        assert readings.get_difference() == 0.0

    def test_iteration(self):
        """Test iterating over cylinder readings."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1250.0)
        readings = Cylinders([reading1, reading2])

        result = []
        for reading in readings:
            result.append(reading)

        assert result == [reading1, reading2]

    def test_indexing(self):
        """Test indexing cylinder readings."""
        reading1 = Cylinder(number=1, value=1200.0)
        reading2 = Cylinder(number=2, value=1250.0)
        readings = Cylinders([reading1, reading2])

        assert readings[0] == reading1
        assert readings[1] == reading2

        with pytest.raises(IndexError):
            readings[2]


class TestRPM:
    """Test cases for the RPM class."""

    def test_default_rpm(self):
        """Test creating RPM with default values."""
        rpm = RPM()
        assert rpm.left is None
        assert rpm.right is None
        assert rpm.computed is None
        assert rpm.difference is None

    def test_rpm_with_values(self):
        """Test creating RPM with specific values."""
        rpm = RPM(left=2400, right=2380, computed=2390)
        assert rpm.left == 2400
        assert rpm.right == 2380
        assert rpm.computed == 2390

    def test_rpm_difference_calculation(self):
        """Test RPM difference calculation."""
        rpm = RPM(left=2400, right=2380)
        assert rpm.difference == 20

        rpm = RPM(left=2380, right=2400)
        assert rpm.difference == 20

    def test_rpm_difference_missing_values(self):
        """Test RPM difference when values are missing."""
        rpm = RPM(left=2400)
        assert rpm.difference is None

        rpm = RPM(right=2400)
        assert rpm.difference is None


class TestFuel:
    """Test cases for the Fuel class."""

    def test_default_fuel(self):
        """Test creating Fuel with default values."""
        fuel = Fuel()
        assert fuel.pressure is None
        assert fuel.flow is None
        assert fuel.quantity is None
        assert fuel.pressure_alert is False
        assert fuel.quantity_alert is False
        assert fuel.has_active_alert is False

    def test_fuel_with_values(self):
        """Test creating Fuel with specific values."""
        fuel = Fuel(pressure=22.5, flow=15.0, quantity=45.0)
        assert fuel.pressure == 22.5
        assert fuel.flow == 15.0
        assert fuel.quantity == 45.0

    def test_fuel_alerts(self):
        """Test fuel alert functionality."""
        fuel = Fuel(pressure_alert=True)
        assert fuel.has_active_alert is True

        fuel = Fuel(quantity_alert=True)
        assert fuel.has_active_alert is True

        fuel = Fuel(pressure_alert=True, quantity_alert=True)
        assert fuel.has_active_alert is True

        fuel = Fuel(pressure_alert=False, quantity_alert=False)
        assert fuel.has_active_alert is False


class TestOil:
    """Test cases for the Oil class."""

    def test_default_oil(self):
        """Test creating Oil with default values."""
        oil = Oil()
        assert oil.pressure is None
        assert oil.temperature is None
        assert oil.pressure_alert is False
        assert oil.temperature_alert is False
        assert oil.has_active_alert is False

    def test_oil_with_values(self):
        """Test creating Oil with specific values."""
        oil = Oil(pressure=60.0, temperature=180.0)
        assert oil.pressure == 60.0
        assert oil.temperature == 180.0

    def test_oil_alerts(self):
        """Test oil alert functionality."""
        oil = Oil(pressure_alert=True)
        assert oil.has_active_alert is True

        oil = Oil(temperature_alert=True)
        assert oil.has_active_alert is True

        oil = Oil(pressure_alert=True, temperature_alert=True)
        assert oil.has_active_alert is True

        oil = Oil(pressure_alert=False, temperature_alert=False)
        assert oil.has_active_alert is False


class TestElectrical:
    """Test cases for the Electrical class."""

    def test_default_electrical(self):
        """Test creating Electrical with default values."""
        electrical = Electrical()
        assert electrical.volts is None
        assert electrical.amps is None

    def test_electrical_with_values(self):
        """Test creating Electrical with specific values."""
        electrical = Electrical(volts=14.2, amps=12.5)
        assert electrical.volts == 14.2
        assert electrical.amps == 12.5

    def test_electrical_zero_values(self):
        """Test Electrical with zero values."""
        electrical = Electrical(volts=0.0, amps=0.0)
        assert electrical.volts == 0.0
        assert electrical.amps == 0.0
