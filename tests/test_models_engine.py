"""
Tests for aerotrace.models.engine module.
"""

import pytest
from aerotrace.models import CylinderReading, CylinderReadings, EngineData


class TestCylinderReading:
    """Test cases for the CylinderReading dataclass."""

    def test_valid_cylinder_reading(self):
        """Test creating a valid cylinder reading."""
        reading = CylinderReading(number=1, value=1200.5)
        assert reading.number == 1
        assert reading.value == 1200.5

    def test_cylinder_number_validation(self):
        """Test validation of cylinder number."""
        # Valid cylinder numbers
        CylinderReading(number=1, value=1200.0)
        CylinderReading(number=6, value=1200.0)

        # Invalid cylinder numbers
        with pytest.raises(ValueError, match="Cylinder number must be >= 1"):
            CylinderReading(number=0, value=1200.0)

        with pytest.raises(ValueError, match="Cylinder number must be >= 1"):
            CylinderReading(number=-1, value=1200.0)

    def test_temperature_value_validation(self):
        """Test validation of temperature values."""
        # Valid numeric values
        CylinderReading(number=1, value=1200)  # int
        CylinderReading(number=1, value=1200.5)  # float
        CylinderReading(number=1, value=0.0)  # zero
        CylinderReading(number=1, value=-10.5)  # negative

        # Invalid non-numeric values
        with pytest.raises(ValueError, match="Temperature value must be numeric"):
            CylinderReading(number=1, value="1200")  # type: ignore

        with pytest.raises(ValueError, match="Temperature value must be numeric"):
            CylinderReading(number=1, value=None)  # type: ignore


class TestCylinderReadings:
    """Test cases for the CylinderReadings collection class."""

    def test_empty_readings(self):
        """Test behavior with empty readings list."""
        readings = CylinderReadings([])
        assert len(readings) == 0
        assert list(readings) == []
        assert readings.get_hottest() is None
        assert readings.get_coolest() is None
        assert readings.get_difference() is None

    def test_single_reading(self):
        """Test behavior with a single reading."""
        reading = CylinderReading(number=1, value=1200.0)
        readings = CylinderReadings([reading])

        assert len(readings) == 1
        assert list(readings) == [reading]
        assert readings[0] == reading
        assert readings.get_hottest() == reading
        assert readings.get_coolest() == reading
        assert readings.get_difference() == 0.0

    def test_multiple_readings(self):
        """Test behavior with multiple readings."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1250.5)
        reading3 = CylinderReading(number=3, value=1180.0)
        readings = CylinderReadings([reading1, reading2, reading3])

        assert len(readings) == 3
        assert list(readings) == [reading1, reading2, reading3]
        assert readings[1] == reading2

    def test_get_hottest(self):
        """Test finding the hottest cylinder."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1250.5)  # hottest
        reading3 = CylinderReading(number=3, value=1180.0)
        readings = CylinderReadings([reading1, reading2, reading3])

        hottest = readings.get_hottest()
        assert hottest is not None
        assert hottest.number == 2
        assert hottest.value == 1250.5

    def test_get_coolest(self):
        """Test finding the coolest cylinder."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1250.5)
        reading3 = CylinderReading(number=3, value=1180.0)  # coolest
        readings = CylinderReadings([reading1, reading2, reading3])

        coolest = readings.get_coolest()
        assert coolest is not None
        assert coolest.number == 3
        assert coolest.value == 1180.0

    def test_get_difference(self):
        """Test calculating temperature difference."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1250.5)  # hottest
        reading3 = CylinderReading(number=3, value=1180.0)  # coolest
        readings = CylinderReadings([reading1, reading2, reading3])

        difference = readings.get_difference()
        assert difference == 70.5  # 1250.5 - 1180.0

    def test_identical_temperatures(self):
        """Test behavior when all temperatures are identical."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1200.0)
        reading3 = CylinderReading(number=3, value=1200.0)
        readings = CylinderReadings([reading1, reading2, reading3])

        # Should return the first one encountered (max/min behavior)
        hottest = readings.get_hottest()
        coolest = readings.get_coolest()
        assert hottest is not None
        assert coolest is not None
        assert hottest.value == 1200.0
        assert coolest.value == 1200.0
        assert readings.get_difference() == 0.0

    def test_iteration(self):
        """Test iterating over cylinder readings."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1250.0)
        readings = CylinderReadings([reading1, reading2])

        result = []
        for reading in readings:
            result.append(reading)

        assert result == [reading1, reading2]

    def test_indexing(self):
        """Test indexing cylinder readings."""
        reading1 = CylinderReading(number=1, value=1200.0)
        reading2 = CylinderReading(number=2, value=1250.0)
        readings = CylinderReadings([reading1, reading2])

        assert readings[0] == reading1
        assert readings[1] == reading2

        with pytest.raises(IndexError):
            readings[2]


class TestEngineData:
    """Test cases for the EngineData dataclass."""

    def test_default_initialization(self):
        """Test creating EngineData with default values."""
        engine_data = EngineData()

        # All optional fields should be None by default
        assert engine_data.rpm is None
        assert engine_data.manifold_pressure is None
        assert engine_data.oil_pressure is None
        assert engine_data.oil_temperature is None
        assert engine_data.fuel_pressure is None
        assert engine_data.volts is None
        assert engine_data.amps is None
        assert engine_data.g_force is None

        # Cylinder readings should be empty collections
        assert len(engine_data.egts) == 0
        assert len(engine_data.chts) == 0

    def test_partial_initialization(self):
        """Test creating EngineData with some values set."""
        engine_data = EngineData(
            rpm=2400.0,
            manifold_pressure=25.5,
            oil_pressure=60.0
        )

        assert engine_data.rpm == 2400.0
        assert engine_data.manifold_pressure == 25.5
        assert engine_data.oil_pressure == 60.0

        # Unspecified fields should still be None
        assert engine_data.oil_temperature is None
        assert engine_data.fuel_pressure is None

    def test_full_initialization(self):
        """Test creating EngineData with all values set."""
        egt_readings = CylinderReadings([
            CylinderReading(number=1, value=1200.0),
            CylinderReading(number=2, value=1220.0)
        ])
        cht_readings = CylinderReadings([
            CylinderReading(number=1, value=380.0),
            CylinderReading(number=2, value=390.0)
        ])

        engine_data = EngineData(
            rpm=2400.0,
            manifold_pressure=25.5,
            egts=egt_readings,
            chts=cht_readings,
            oil_pressure=60.0,
            oil_temperature=180.0,
            fuel_pressure=22.0,
            volts=14.2,
            amps=12.5,
            g_force=1.2
        )

        assert engine_data.rpm == 2400.0
        assert engine_data.manifold_pressure == 25.5
        assert engine_data.egts == egt_readings
        assert engine_data.chts == cht_readings
        assert engine_data.oil_pressure == 60.0
        assert engine_data.oil_temperature == 180.0
        assert engine_data.fuel_pressure == 22.0
        assert engine_data.volts == 14.2
        assert engine_data.amps == 12.5
        assert engine_data.g_force == 1.2

    def test_cylinder_readings_integration(self):
        """Test integration with CylinderReadings in EngineData."""
        egt_readings = CylinderReadings([
            CylinderReading(number=1, value=1200.0),
            CylinderReading(number=2, value=1250.0),
            CylinderReading(number=3, value=1180.0)
        ])

        engine_data = EngineData(egts=egt_readings)

        # Test that we can access CylinderReadings methods
        assert len(engine_data.egts) == 3
        hottest = engine_data.egts.get_hottest()
        coolest = engine_data.egts.get_coolest()
        assert hottest is not None
        assert coolest is not None
        assert hottest.number == 2
        assert coolest.number == 3
        assert engine_data.egts.get_difference() == 70.0

    def test_negative_values_allowed(self):
        """Test that negative values are allowed where appropriate."""
        engine_data = EngineData(
            g_force=-0.5,  # Negative G-force should be allowed
            oil_temperature=-10.0  # Extreme cold temperatures
        )

        assert engine_data.g_force == -0.5
        assert engine_data.oil_temperature == -10.0

    def test_zero_values_allowed(self):
        """Test that zero values are handled correctly."""
        engine_data = EngineData(
            rpm=0.0,
            manifold_pressure=0.0,
            oil_pressure=0.0,
            volts=0.0,
            amps=0.0,
            g_force=0.0
        )

        assert engine_data.rpm == 0.0
        assert engine_data.manifold_pressure == 0.0
        assert engine_data.oil_pressure == 0.0
        assert engine_data.volts == 0.0
        assert engine_data.amps == 0.0
        assert engine_data.g_force == 0.0