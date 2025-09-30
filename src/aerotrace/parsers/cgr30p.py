"""Parser for Electronics International CGR-30P Engine Monitoring System data.

The CGR-30P exports CSV files with metadata in the first 14 lines, followed by
header row on line 14 and data starting from line 15.

Example usage:
    >>> from aerotrace.parsers import cgr30p
    >>>
    >>> # Stream processing (memory efficient)
    >>> for engine_data in cgr30p.parse_file('flight_data.csv'):
    ...     print(f"RPM Left: {engine_data.rpm.left}")
    >>>
    >>> # Convert to list if needed
    >>> engine_data_list = list(cgr30p.parse_file('flight_data.csv'))
    >>> print(f"Parsed {len(engine_data_list)} data points")
    >>>
    >>> # Parse individual row (if you have CSV data already loaded)
    >>> row_dict = {'RPMLEFT': '2400', 'RPMRIGHT': '2380', 'SEL TANK QTY': 'TOTAL   : 45.2'}
    >>> engine_data = cgr30p.parse_dict(row_dict)
    >>> print(f"Left RPM: {engine_data.rpm.left}")
"""

import csv
import logging
import re
from pathlib import Path
from typing import Dict, Iterator, Optional, Union

from ..models import engine

# Constants
DATA_START_LINE = 15

# Logger
logger = logging.getLogger(__name__)

# Public API
__all__ = ["parse_file", "parse_dict"]


def _get_float(data: Dict[str, str], key: str) -> Optional[float]:
    """Extract and convert parameter to float from data dictionary

    Args:
        data: Row data dictionary from CSV
        key: Column name to extract

    Returns:
        Float value or None if conversion fails or value is empty
    """
    value = data.get(key, "").strip()
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def _get_int(data: Dict[str, str], key: str) -> Optional[int]:
    """Extract and convert parameter to int from data dictionary

    Args:
        data: Row data dictionary from CSV
        key: Column name to extract

    Returns:
        Integer value or None if conversion fails or value is empty
    """
    value = data.get(key, "").strip()
    if not value:
        return None

    try:
        return int(float(value))
    except ValueError:
        return None


def _parse_tank_quantity(data: Dict[str, str], key: str) -> Optional[float]:
    """Parse fuel tank quantity from CGR-30P format

    The CGR-30P exports tank quantity in format "TOTAL   : 68.16". This function
    extracts the numeric value using a compiled regex pattern for better performance.

    Args:
        data: Row data dictionary from CSV
        key: Column name to extract (typically 'SEL TANK QTY')

    Returns:
        Numeric fuel quantity in liters, or None if parsing fails
    """
    tank_qty_str = data.get(key, "").strip()
    if not tank_qty_str:
        return None

    match = re.search(r":\s*(\d+(?:\.\d+)?)", tank_qty_str)
    if match:
        return float(match.group(1))

    return None


def _parse_cylinders(
    data: Dict[str, str], prefix: str, count: int = 6
) -> engine.Cylinders:
    """Parse cylinder temperature data (EGT or CHT)

    Args:
        data: Row data dictionary from CSV
        prefix: Column prefix ('EGT' or 'CHT')
        count: Number of cylinders to parse (default 6)

    Returns:
        Cylinders object containing all valid temperature readings
    """
    readings = []

    for i in range(1, count + 1):
        temp_value = _get_float(data, f"{prefix}{i};*F")

        if temp_value is not None:
            readings.append(engine.Cylinder(number=i, value=temp_value))

    return engine.Cylinders(readings)


def parse_dict(data: Dict[str, str]) -> engine.EngineData:
    """Parse a single row of CGR-30P data from a dictionary

    Args:
        data: Dictionary with CSV column names as keys and cell values as strings

    Returns:
        EngineData object with all parsed engine parameters
    """
    rpm = engine.RPM(
        left=_get_int(data, "RPMLEFT;RPM"),
        right=_get_int(data, "RPMRIGHT;RPM"),
        computed=_get_int(data, "RPM;***"),
    )

    fuel = engine.Fuel(
        pressure=_get_float(data, "FUEL P;PSI"),
        flow=_get_float(data, "FLOW;LPH"),
        quantity=_parse_tank_quantity(data, "SEL TANK QTY"),
    )

    oil = engine.Oil(
        pressure=_get_float(data, "OIL P;PSI"), temperature=_get_float(data, "OIL T;*F")
    )

    electrical = engine.Electrical(
        volts=_get_float(data, "VOLTS;V"), amps=_get_float(data, "AMPS;A")
    )

    return engine.EngineData(
        rpm=rpm,
        manifold_pressure=_get_float(data, "MP;InHg"),
        egts=_parse_cylinders(data, "EGT"),
        chts=_parse_cylinders(data, "CHT"),
        fuel=fuel,
        oil=oil,
        electrical=electrical,
        g_force=_get_float(data, "G METR;G"),
    )


def parse_file(file_path: Union[str, Path]) -> Iterator[engine.EngineData]:
    """Parse a CGR-30P CSV file and yield EngineData objects

    The function automatically skips the metadata lines and yields
    each data row as it's processed. Invalid rows are logged but don't stop processing.

    Args:
        file_path: Path to the CGR-30P CSV file (string or Path object)

    Yields:
        EngineData objects, one per valid data row

    Raises:
        FileNotFoundError: If the specified file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as file:
        for _ in range(DATA_START_LINE - 1):
            next(file)

        reader = csv.DictReader(file)

        for row_num, row in enumerate(reader, start=DATA_START_LINE):
            try:
                engine_data = parse_dict(row)
                yield engine_data
            except Exception as e:
                logger.warning("Error parsing row %d: %s", row_num, e)
                continue
