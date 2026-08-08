# UVI Test Suite

This directory contains comprehensive unit tests for the UVI (Unified Verb Index) package.

## Running Tests

### Method 1: Using the Test Runner (Recommended)
```bash
python run_tests.py
```

### Method 2: Using unittest directly
```bash
python -m unittest tests.test_uvi_loading -v
```

### Method 3: Using pytest (if installed)
```bash
pytest tests/ -v
```

## Test Structure

### `test_uvi_loading.py`
Comprehensive unit tests covering:

- **TestUVIInitialization**: UVI class initialization with different parameters
- **TestUVICorpusPathSetup**: Corpus path detection and configuration
- **TestUVICorpusLoading**: Corpus loading functionality and error handling
- **TestUVIVerbNetParsing**: VerbNet XML parsing with real XML samples
- **TestUVIUtilityMethods**: Utility methods for corpus management
- **TestUVIPackageLevel**: Package-level functionality and imports

## Test Coverage

The test suite includes **16 comprehensive tests** covering:

- ✅ UVI class initialization (with/without loading)
- ✅ Corpus path auto-detection with flexible directory naming
- ✅ Error handling for missing corpus files
- ✅ VerbNet XML parsing with complete class extraction
- ✅ Utility methods for corpus status and information
- ✅ Package-level imports and metadata
- ✅ Mock-based testing to avoid file system dependencies

## Test Features

- **Mock-based**: Uses `unittest.mock` to avoid file system dependencies
- **Comprehensive**: Tests all major functionality without requiring actual corpus files
- **Real XML Parsing**: Includes actual VerbNet XML samples for parser testing
- **Error Handling**: Tests both success and failure scenarios
- **Package Integration**: Verifies package-level functionality

## Test Output

Example successful test run:
```
============================================================
UVI (Unified Verb Index) - Test Suite
============================================================

Running UVI unit tests...

test_init_without_loading ... ok
test_load_verbnet_success ... ok
test_parse_verbnet_class ... ok
... (all 16 tests) ...

----------------------------------------------------------------------
Ran 16 tests in 0.014s

OK

============================================================
Test Results Summary
============================================================
Tests run: 16
Failures: 0
Errors: 0
Skipped: 0

[SUCCESS] ALL TESTS PASSED
The UVI package is functioning correctly!
============================================================
```

## Adding New Tests

To add new tests:

1. Create new test methods in existing test classes, or
2. Create new test classes inheriting from `unittest.TestCase`
3. Follow the naming convention: `test_*` for methods and `Test*` for classes
4. Use mocks to avoid file system dependencies where appropriate
5. Run the test suite to ensure all tests pass

The test suite is designed to be comprehensive yet fast, ensuring the UVI package functions correctly without requiring the full corpus file structure.