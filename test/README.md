# Test Organization Guide

This directory contains all demo and test files for the Stock Analysis System, organized into logical categories for better maintainability.

## Directory Structure

### `/demos/`
Demo scripts showcasing specific features and capabilities:
- `demo_enhanced.py` - Enhanced features demonstration
- `demo_financial_dashboard.py` - Financial dashboard showcase
- `demo_quarterly_analysis.py` - Quarterly analysis features
- `demo_stock_display.py` - Stock display functionality

### `/unit/`
Unit tests for individual components and functions:
- `test_app.py` - Application component tests
- `test_main.py` - Main module tests
- `test_modification.py` - Code modification tests
- `test_network_fix.py` - Network functionality tests

### `/integration/`
Integration tests covering end-to-end workflows:
- `comprehensive_test.py` - Comprehensive system testing
- `extensive_test_suite.py` - Extended test coverage
- `final_system_test.py` - Final system validation
- `frontend_test.py` - Frontend integration tests
- `full_test.py` - Full system workflow tests
- `system_test.py` - Core system functionality
- `ui_test.py` - User interface tests
- `ultimate_test.py` - Ultimate system validation

### `/debug/`
Debug and troubleshooting scripts:
- `test_akshare_calls.py` - AKshare API call testing
- `test_cached_data_fix.py` - Cache data validation
- `test_data_type_fix.py` - Data type handling tests
- `test_encoding_fix.py` - Encoding issue resolution

## Running Tests

### Run All Tests
```bash
# From project root
python -m pytest test/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest test/unit/ -v

# Integration tests only
python -m pytest test/integration/ -v

# Demo scripts (manual execution)
python test/demos/demo_financial_dashboard.py
```

### Run Individual Tests
```bash
python test/integration/comprehensive_test.py
python test/debug/test_akshare_calls.py
```

## Test Organization Principles

1. **Separation of Concerns**: Each directory has a specific purpose
2. **Easy Navigation**: Related tests are grouped together
3. **Scalability**: New tests can be easily added to appropriate categories
4. **Maintainability**: Clear structure makes it easy to find and update tests
5. **Documentation**: Each category is documented for quick reference

## Adding New Tests

When adding new test files:
1. Determine the appropriate category (demo, unit, integration, debug)
2. Place the file in the corresponding directory
3. Update this README if adding a new category or significant test type
4. Follow naming conventions: `test_*.py` for tests, `demo_*.py` for demos

## Best Practices

- Keep test files focused on specific functionality
- Use descriptive names that indicate what is being tested
- Include docstrings explaining the test purpose
- Ensure tests are independent and can run in any order
- Update tests when corresponding functionality changes