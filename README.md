# L5X-ST Compiler

A modern Python 3 implementation for converting between L5X files (Allen Bradley/Rockwell Automation) and Structured Text (ST) format. This project builds upon the original L5X parser and provides a clean, modular, and testable codebase with **complete round-trip conversion** and **IR validation**.

## Features

### L5X to Structured Text (L5X2ST)
- Convert single L5X files to ST format
- Convert entire directories of L5X files to consolidated ST
- Handle multiple PLCs with proper variable renaming
- Support for Function Block Diagrams (FBD)
- Support for Ladder Logic (RLL)
- Automatic type conversion and reserved word handling
- Message instruction handling
- Timer function block support
- **IR validation mode** with guardrails

### Structured Text to L5X (ST2L5X)
- Convert ST files back to L5X format
- Generate proper L5X XML structure
- Support for variable declarations
- Support for function declarations
- Support for struct declarations
- **IR validation mode** with fidelity scoring

### Advanced Features
- **Complete Round-Trip Conversion**: L5X ↔ ST ↔ L5X with validation
- **Intermediate Representation (IR)**: Internal data model for validation
- **Fidelity Scoring**: Quantitative measurement of conversion quality
- **Guardrail Validation**: Optional `--use-ir` flag for enhanced validation
- **Industrial-Grade Reliability**: Handles complex Rockwell automation projects

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Install from source
```bash
git clone <repository-url>
cd l5x2ST
pip install -e .
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Convert L5X to ST
```bash
# Convert single file
python -m l5x_st_compiler.cli l5x2st -i project.L5X -o output.st

# With IR validation (recommended)
python -m l5x_st_compiler.cli l5x2st -i project.L5X -o output.st --use-ir

# With verbose output
python -m l5x_st_compiler.cli l5x2st -i project.L5X -o output.st -v
```

#### Convert ST to L5X
```bash
# Convert single file
python -m l5x_st_compiler.cli st2l5x -i program.st -o output.L5X

# With IR validation (recommended)
python -m l5x_st_compiler.cli st2l5x -i program.st -o output.L5X --use-ir

# With verbose output
python -m l5x_st_compiler.cli st2l5x -i program.st -o output.L5X -v
```

### Python API

#### L5X to ST Conversion
```python
from l5x_st_compiler import L5X2STConverter

converter = L5X2STConverter()

# Convert single file
converter.convert_file("project.L5X", "output.st")

# Parse and get STFile object
st_file = converter.parse_l5x_file("project.L5X")
print(str(st_file))
```

#### ST to L5X Conversion
```python
from l5x_st_compiler import ST2L5XConverter

converter = ST2L5XConverter()

# Convert single file
converter.convert_file("program.st", "output.L5X")

# Parse and get L5XElement object
l5x_project = converter.parse_st_file("program.st")
```

#### IR Validation and Round-Trip
```python
from l5x_st_compiler.ir_converter import IRConverter
from l5x_st_compiler import L5X2STConverter, ST2L5XConverter

# Load and validate L5X
ir_converter = IRConverter()
l5x2st = L5X2STConverter()
st2l5x = ST2L5XConverter()

# Round-trip with validation
original_project = l5x2st.parse_l5x_file("project.L5X")
original_ir = ir_converter.l5x_to_ir(original_project)

# Convert to ST and back
st_content = str(original_project)
final_l5x = st2l5x.convert_st_to_l5x(st_content, "")
final_project = l5x2st.parse_l5x_file("final.L5X")
final_ir = ir_converter.l5x_to_ir(final_project)

# Calculate fidelity score
fidelity_score = ir_converter.calculate_fidelity_score(original_ir, final_ir)
print(f"Round-trip fidelity: {fidelity_score:.2%}")
```

## Project Structure

```
l5x2ST/
├── l5x_st_compiler/          # Main package
│   ├── __init__.py           # Package initialization
│   ├── constants.py          # Constants and configurations
│   ├── models.py             # Data models and IR classes
│   ├── utils.py              # Utility functions
│   ├── instructions.py       # Instruction processors
│   ├── ladder_logic.py       # Ladder logic translator
│   ├── fbd_translator.py     # FBD to ST translator
│   ├── ir_converter.py       # IR conversion system
│   ├── l5x2st.py            # L5X to ST converter
│   ├── st2l5x.py            # ST to L5X converter
│   └── cli.py               # Command-line interface
├── examples/                 # Example scripts
│   ├── basic_usage.py       # Basic usage examples
│   ├── complex_st_example.py # Complex ST example
│   ├── ir_roundtrip_test.py # IR round-trip testing
│   ├── l5x_compare.py       # L5X comparison tool
│   └── validation_test.py   # Comprehensive validation
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_l5x2st.py       # Tests for L5X2ST converter
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── pytest.ini               # Pytest configuration
└── README.md                # This file
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=l5x_st_compiler

# Run specific test file
pytest tests/test_l5x2st.py

# Run with verbose output
pytest -v

# Run validation test suite
python examples/validation_test.py
```

### Code Quality
```bash
# Format code with black
black l5x_st_compiler/

# Lint with flake8
flake8 l5x_st_compiler/

# Type checking with mypy
mypy l5x_st_compiler/
```

### Building and Installing
```bash
# Install in development mode
pip install -e .

# Build distribution
python setup.py sdist bdist_wheel

# Install from distribution
pip install dist/l5x-st-compiler-2.0.0.tar.gz
```

## Key Improvements Over Original

### Code Quality
- **Python 3 Support**: Full Python 3.8+ compatibility
- **Type Hints**: Comprehensive type annotations
- **Modular Design**: Clean separation of concerns
- **Error Handling**: Proper exception handling and user feedback
- **Documentation**: Comprehensive docstrings and comments

### Architecture
- **Object-Oriented**: Proper class-based design
- **State Management**: Centralized compiler state
- **Configuration**: Externalized constants and settings
- **Extensibility**: Easy to add new features and processors
- **IR System**: Intermediate representation for validation

### Testing
- **Unit Tests**: Comprehensive test coverage
- **Mock Support**: Proper mocking for external dependencies
- **Test Configuration**: Pytest configuration and markers
- **CI/CD Ready**: Structured for continuous integration
- **Validation Suite**: Comprehensive round-trip testing

### Features
- **Bidirectional Conversion**: Both L5X→ST and ST→L5X
- **CLI Interface**: User-friendly command-line tools with IR validation
- **API Support**: Programmatic access to converters
- **IR Validation**: Guardrail system for conversion quality
- **Fidelity Scoring**: Quantitative measurement of round-trip accuracy

## Supported Instructions

The compiler supports a comprehensive set of Rockwell Automation instructions. For the complete instruction reference, see the official [Logix 5000 Controllers General Instructions](https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1756-rm003_-en-p.pdf) manual.

### Currently Supported Categories
- **Bit Instructions**: XIC, XIO, OTE, OTL, OTU, ONS, OSR, OSF, OSRI, OSFI
- **Timer Instructions**: TON, TONR, TOF, TOFR, RTO, RTOR
- **Counter Instructions**: CTU, CTD, CTUD, RES
- **Compare Instructions**: EQ, NE, GT, GE, LT, LE, CMP, LIMIT, MEQ
- **Math Instructions**: ADD, SUB, MUL, DIV, MOD, SQR, SQRT, ABS, NEG
- **Data Conversion**: TOD, FRD, DTD, DTR, ROUND, TRUNC
- **Control Instructions**: JMP, JSR, RET, FOR, NEXT, WHILE, REPEAT, IF, CASE
- **Message Instructions**: MSG
- **System Instructions**: GSV, SSV

## Dependencies

### Core Dependencies
- `l5x>=0.1.0`: L5X file parser
- `ordered-set>=4.0.0`: Ordered set implementation
- `lxml>=4.6.0`: XML processing
- `click>=8.0.0`: CLI framework

### Development Dependencies
- `pytest>=6.0.0`: Testing framework
- `pytest-cov>=2.10.0`: Coverage reporting
- `black>=21.0.0`: Code formatting
- `flake8>=3.8.0`: Code linting
- `mypy>=0.800`: Type checking

## Limitations and TODOs

### Current Limitations
- Some complex FBD structures may not convert perfectly
- Message instruction handling is simplified
- Limited support for advanced motion instructions

### Planned Improvements
- [ ] Enhanced FBD processing with more complex structures
- [ ] Better message instruction handling
- [ ] Support for more advanced motion instructions
- [ ] Performance optimizations for large projects
- [ ] Better error reporting and diagnostics
- [ ] Integration with OpenPLC for ST validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original L5X parser and converter code
- Rockwell Automation for L5X format and instruction documentation
- IEC 61131-3 standard for Structured Text specification

## Support

For issues, questions, or contributions, please use the project's issue tracker or contact the maintainers.