# AeroTrace Parsers

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/aerotrace-parsers.svg)](https://badge.fury.io/py/aerotrace-parsers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for parsing aircraft Engine Monitoring System (EMS) telemetry data into standardized formats for real-time monitoring and analysis.

## Supported EMS Types
| EMS Type | Status | Description |
|----------|--------|-------------|
| E.I CGR-30P  | 🚧 In Progress | Electronics International CGR-30P Primary |

## Installation
```bash
pip install aerotrace-parsers
```

## Quick Start
```python
from aerotrace.parsers import cgr30p

# Parse real CGR-30P flight data from an example file
for engine_data in cgr30p.parse_file('docs/example-cgr30p-flight-data.csv'):
    print(f"RPM: {engine_data.rpm.left}/{engine_data.rpm.right}")
    print(f"Fuel: {engine_data.fuel.quantity}L")
    # ... process engine data
```

## Development
### Setup
```bash
git clone https://github.com/alexc/aerotrace-parsers.git
cd aerotrace-parsers
make install
```

### Running Tests
```bash
make test
```

### Code Quality
```bash
make lint
make format
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
