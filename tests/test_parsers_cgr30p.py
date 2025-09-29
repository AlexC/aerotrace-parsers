"""
Tests for aerotrace.parsers.cgr30p module.
"""

import pytest
from pathlib import Path

from aerotrace.parsers import cgr30p


def _create_cgr30p_csv(data_rows):
    """Helper function to create a CGR30P CSV with proper headers and data rows."""
    header = """Electronics International Inc
CGR-30P Flight Data Recording
Aircraft ID: G-TEST

Unit ID....: 10001923
EDC Models.: P-4-6-G,,
SW: Release, Date: Apr  3 2019, Version: 1.2-296
Local Time: 2024/11/17 11:53:32
Zulu Time.: 2024/11/17 11:53:32
Flight Number: 440
Engine Hours.:   3.05 hrs
Tach Time....:   1.62 hrs
Data Logging Interval: 0.3 sec

TIME,SEL TANK QTY,RPMLEFT;RPM,RPMRIGHT;RPM,RPM;***,MP;InHg,TEMP COMP;*F,VOLTS;V,AMPS;A,FLOW;LPH,EGT1;*F,EGT2;*F,EGT3;*F,EGT4;*F,EGT5;*F,EGT6;*F,EGT:;***,EGT-D:;***,EGT-H:;***,CHT1;*F,CHT2;*F,CHT3;*F,CHT4;*F,CHT5;*F,CHT6;*F,CHT:;***,CHT-D:;***,CHT-H:;***,FUEL;L,FUEL     ANN;L,FUEL P;PSI,FUEL P   ANN;PSI,OIL P;PSI,OIL P    ANN;PSI,OIL T;*F,OIL T    ANN;*F,G METR;G,FLT;HRS,TACH;HRS,EST  TOTAL;L,RANGE;NM,TO DEST;NM,AT DEST;NM,REMAIN;L,TO DEST;L,AT DEST;L,TO EMPTY;H:M,TO DEST;H:M,AT DEST;H:M,DISTANCE;NM,TIME;H:M,QUANTITY;L,FLIGHT;L,SINCE ADD;L,ECONOMY;MPL,ENGINE;LPH,SWITCH IN;H:M,SWTCH    ANN; ,FUEL     ANN; ,"""

    if isinstance(data_rows, str):
        data_rows = [data_rows]

    return header + "\n" + "\n".join(data_rows)


class TestParseFile:
    """Test cases for parse_file function."""

    @pytest.fixture
    def test_data_dir(self):
        """Path to test data directory."""
        return Path(__file__).parent / "data"

    def test_parse_basic_file_count(self, test_data_dir):
        """Test that basic CGR30P file parses correct number of rows."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))
        assert len(engine_data_list) == 3

    def test_rpm_data_parsing(self, test_data_dir):
        """Test RPM data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        # Engine off
        assert engine_data_list[0].rpm.left == 0
        assert engine_data_list[0].rpm.right == 0
        assert engine_data_list[0].rpm.computed == 0
        assert engine_data_list[0].rpm.difference == 0

        # Engine running at 1000 RPM
        assert engine_data_list[1].rpm.left == 1000
        assert engine_data_list[1].rpm.right == 1000
        assert engine_data_list[1].rpm.computed == 1000
        assert engine_data_list[1].rpm.difference == 0

        # Higher RPM
        assert engine_data_list[2].rpm.left == 1050
        assert engine_data_list[2].rpm.right == 1050
        assert engine_data_list[2].rpm.computed == 1050
        assert engine_data_list[2].rpm.difference == 0

    def test_manifold_pressure_parsing(self, test_data_dir):
        """Test manifold pressure parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        assert engine_data_list[0].manifold_pressure == 29.9
        assert engine_data_list[1].manifold_pressure == 17.4
        assert engine_data_list[2].manifold_pressure == 15.6

    def test_fuel_system_parsing(self, test_data_dir):
        """Test fuel system data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        # Engine off
        assert engine_data_list[0].fuel.quantity == 68.16
        assert engine_data_list[0].fuel.pressure == 0.0
        assert engine_data_list[0].fuel.flow == 0

        # Engine running
        assert engine_data_list[1].fuel.quantity == 68.06
        assert engine_data_list[1].fuel.pressure == 42
        assert engine_data_list[1].fuel.flow == 20

        # Higher power
        assert engine_data_list[2].fuel.quantity == 68.06
        assert engine_data_list[2].fuel.pressure == 43
        assert engine_data_list[2].fuel.flow == 18

    def test_oil_system_parsing(self, test_data_dir):
        """Test oil system data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        # Engine off
        assert engine_data_list[0].oil.pressure == 25
        assert engine_data_list[0].oil.temperature == 25

        # Engine running
        assert engine_data_list[1].oil.pressure == 70
        assert engine_data_list[1].oil.temperature == 46

        # Higher power
        assert engine_data_list[2].oil.pressure == 87
        assert engine_data_list[2].oil.temperature == 46

    def test_electrical_system_parsing(self, test_data_dir):
        """Test electrical system data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        # All rows should have consistent electrical readings
        assert engine_data_list[0].electrical.volts == 13.3
        assert engine_data_list[0].electrical.amps == 1.3
        assert engine_data_list[1].electrical.volts == 13.1
        assert engine_data_list[1].electrical.amps == 2.5
        assert engine_data_list[2].electrical.volts == 13.2
        assert engine_data_list[2].electrical.amps == 1.8

    def test_g_force_parsing(self, test_data_dir):
        """Test G-force data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        assert engine_data_list[0].g_force == 1.0
        assert engine_data_list[1].g_force == 2.4
        assert engine_data_list[2].g_force == 1.1

    def test_egt_cylinder_parsing(self, test_data_dir):
        """Test EGT cylinder data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        # Engine off - all cylinders should be parsed
        assert len(engine_data_list[0].egts) == 6
        expected_egts_off = [30, 31, 32, 33, 34, 35]
        for i, expected_temp in enumerate(expected_egts_off):
            assert engine_data_list[0].egts[i].number == i + 1
            assert engine_data_list[0].egts[i].value == expected_temp

        # Engine running - higher temperatures
        assert len(engine_data_list[1].egts) == 6
        expected_egts_running = [235, 252, 239, 24, 237, 238]
        for i, expected_temp in enumerate(expected_egts_running):
            assert engine_data_list[1].egts[i].number == i + 1
            assert engine_data_list[1].egts[i].value == expected_temp

        # Higher power - even higher temperatures
        assert len(engine_data_list[2].egts) == 6
        expected_egts_high = [452, 484, 456, 38, 423, 445]
        for i, expected_temp in enumerate(expected_egts_high):
            assert engine_data_list[2].egts[i].number == i + 1
            assert engine_data_list[2].egts[i].value == expected_temp

    def test_cht_cylinder_parsing(self, test_data_dir):
        """Test CHT cylinder data parsing across all engine states."""
        file_path = test_data_dir / "cgr30p_test_basic.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        # Engine off
        assert len(engine_data_list[0].chts) == 6
        expected_chts_off = [20, 21, 22, 23, 24, 25]
        for i, expected_temp in enumerate(expected_chts_off):
            assert engine_data_list[0].chts[i].number == i + 1
            assert engine_data_list[0].chts[i].value == expected_temp

        # Engine running
        assert len(engine_data_list[1].chts) == 6
        expected_chts_running = [40, 41, 42, 43, 44, 45]
        for i, expected_temp in enumerate(expected_chts_running):
            assert engine_data_list[1].chts[i].number == i + 1
            assert engine_data_list[1].chts[i].value == expected_temp

        # Higher power
        assert len(engine_data_list[2].chts) == 6
        expected_chts_high = [50, 51, 52, 53, 54, 55]
        for i, expected_temp in enumerate(expected_chts_high):
            assert engine_data_list[2].chts[i].number == i + 1
            assert engine_data_list[2].chts[i].value == expected_temp

    def test_parse_empty_data_file(self, test_data_dir):
        """Test parsing a file with no data rows."""
        file_path = test_data_dir / "cgr30p_test_empty.csv"
        engine_data_list = list(cgr30p.parse_file(file_path))

        assert len(engine_data_list) == 0

    def test_file_not_found(self):
        """Test error handling for non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            list(cgr30p.parse_file("nonexistent_file.csv"))

    def test_invalid_numeric_data(self, tmp_path):
        """Test handling of invalid numeric values."""
        data_row = "11:53:32,INVALID_QTY,abc,def,ghi,invalid,85,text,not_numeric,text,47,47,47,46,47,47,47,1,47,46,46,46,46,46,46,46,1,46,67,67,42,42,0,0,46,46,1.0,  0.00,  1.62,68,0.0,0.0,0.0,68,0,0, 99:59,  0:00,  0:00,0.0, 99:59,0,0,0,0.0,0,0,100.0,68,"

        test_file = tmp_path / "test_invalid_numeric.csv"
        test_file.write_text(_create_cgr30p_csv(data_row))

        engine_data_list = list(cgr30p.parse_file(test_file))
        assert len(engine_data_list) == 1

        data = engine_data_list[0]
        assert data.rpm.left is None  # "abc" should be None
        assert data.rpm.right is None  # "def" should be None
        assert data.rpm.computed is None  # "ghi" should be None
        assert data.manifold_pressure is None  # "invalid" should be None
        assert data.fuel.quantity is None  # "INVALID_QTY" should be None
        assert data.electrical.amps is None  # "not_numeric" should be None
        assert data.fuel.flow is None  # "text" should be None

    def test_float_to_int_conversion(self, tmp_path):
        """Test that float values are properly converted to integers for RPM."""
        data_row = "11:53:32,LEFT    : 25.5,2400.7,2380.3,2390.9,22.8,85,14.2,0.0,75.5,1100,1150,1175,1200,1250,1300,1200,50,1300,300,320,350,400,425,450,400,50,450,70,70,42,42,60,60,180,46,0.8,  0.01,  1.63,25.5,0.0,60.0,0.0,180,0.0,0.8, 99:58,  0:00,  0:00,0.0, 99:58,0,0,0,0.0,75.5,0,100.0,25.5,"

        test_file = tmp_path / "test_float_conversion.csv"
        test_file.write_text(_create_cgr30p_csv(data_row))

        engine_data_list = list(cgr30p.parse_file(test_file))
        assert len(engine_data_list) == 1

        data = engine_data_list[0]
        assert data.rpm.left == 2400  # 2400.7 truncated to int
        assert data.rpm.right == 2380  # 2380.3 truncated to int
        assert data.rpm.computed == 2390  # 2390.9 truncated to int
        assert data.fuel.quantity == 25.5  # Float preserved for fuel quantity

    def test_negative_values(self, tmp_path):
        """Test handling of negative values."""
        data_row = "11:53:32,TOTAL   : 45.2,1000,1000,1000,22.8,85,14.2,-5.0,75.5,1100,1150,1175,1200,1250,1300,1200,50,1300,300,320,350,400,425,450,400,50,450,70,70,42,42,60,60,180,46,-1.2,  0.01,  1.63,45.2,0.0,60.0,0.0,180,0.0,-5.0, 99:58,  0:00,  0:00,0.0, 99:58,0,0,0,0.0,75.5,0,100.0,45.2,"

        test_file = tmp_path / "test_negative_values.csv"
        test_file.write_text(_create_cgr30p_csv(data_row))

        engine_data_list = list(cgr30p.parse_file(test_file))
        assert len(engine_data_list) == 1

        data = engine_data_list[0]
        assert data.electrical.amps == -5.0  # Negative values should be preserved
        assert data.g_force == -1.2  # Negative G-force should be preserved

    def test_partial_cylinder_data(self, tmp_path):
        """Test handling of missing cylinder data."""
        data_row = "11:53:32,TOTAL   : 45.2,2400,2380,2400,25.8,85,12.8,2.5,85,1100,,1200,1250,,1300,1200,50,1300,300,,350,400,,450,400,50,450,70,70,42,42,60,60,180,46,1.2,  0.01,  1.63,45.2,0.0,60.0,0.0,180,0.0,2.5, 99:58,  0:00,  0:00,0.0, 99:58,0,0,0,0.0,85,0,100.0,45.2,"

        test_file = tmp_path / "test_partial_cylinders.csv"
        test_file.write_text(_create_cgr30p_csv(data_row))

        engine_data_list = list(cgr30p.parse_file(test_file))
        assert len(engine_data_list) == 1

        data = engine_data_list[0]
        # Should only parse cylinders with valid data (missing EGT2, EGT5, CHT2, CHT5)
        assert len(data.egts) == 4  # 1, 3, 4, 6
        assert len(data.chts) == 4  # 1, 3, 4, 6

        # Verify the cylinders that are present have correct numbers and values
        assert data.egts[0].number == 1
        assert data.egts[0].value == 1100
        assert data.egts[1].number == 3
        assert data.egts[1].value == 1200

    def test_empty_and_zero_values(self, tmp_path):
        """Test handling of empty strings and zero values."""
        data_row = "11:53:32,,0,,0,0.0,0,,,,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.0,  0.00,  1.62,0,0.0,0.0,0.0,0,0,0, 99:59,  0:00,  0:00,0.0, 99:59,0,0,0,0.0,0,0,100.0,0,"

        test_file = tmp_path / "test_empty_zero.csv"
        test_file.write_text(_create_cgr30p_csv(data_row))

        engine_data_list = list(cgr30p.parse_file(test_file))
        assert len(engine_data_list) == 1

        data = engine_data_list[0]
        assert data.rpm.left == 0  # Zero values should be preserved
        assert data.rpm.right is None  # Empty string should be None
        assert data.fuel.quantity is None  # Empty tank quantity string
        assert data.manifold_pressure == 0.0  # Zero float preserved
        assert len(data.egts) == 6  # All cylinders present even with zero values
        assert len(data.chts) == 6  # All cylinders present even with zero values
        # Verify all EGT and CHT values are zero
        for cylinder in data.egts:
            assert cylinder.value == 0.0
        for cylinder in data.chts:
            assert cylinder.value == 0.0

    def test_malformed_row_exception_handling(self, tmp_path):
        """Test that malformed rows are handled gracefully with logging."""
        # Create a valid data row and a malformed row
        valid_row = "11:53:32,TOTAL   : 68.16,2400,2380,2390,28.5,85,13.3,1.3,20,347,347,347,346,347,347,347,1,347,146,146,146,146,146,146,146,1,146,67,67,42,42,0,0,25,25,1.0,  0.00,  1.62,68,0.0,0.0,0.0,68,0,0, 99:59,  0:00,  0:00,0.0, 99:59,0,0,0,0.0,0,0,100.0,68,"
        malformed_row = "11:53:33,MALFORMED"  # Missing most columns

        test_file = tmp_path / "test_malformed.csv"
        test_file.write_text(_create_cgr30p_csv([valid_row, malformed_row]))

        # This should yield only the valid row, skipping the malformed one
        engine_data_list = list(cgr30p.parse_file(test_file))
        assert len(engine_data_list) == 1

        # Verify the valid row was parsed correctly
        data = engine_data_list[0]
        assert data.fuel.quantity == 68.16
        assert data.rpm.left == 2400
