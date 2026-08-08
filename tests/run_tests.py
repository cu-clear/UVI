#!/usr/bin/env python3
"""
Comprehensive Test Runner for UVI Package

This script provides both simple and advanced test running capabilities for the
UVI (Unified Verb Index) package. It supports coverage analysis, different test
types, and multiple output formats.

Usage:
    python tests/run_tests.py [options]

Simple usage (runs all tests):
    python tests/run_tests.py

Advanced options:
    --coverage    Run tests with coverage analysis
    --verbose     Run tests with verbose output
    --integration Run only integration tests
    --unit        Run only unit tests
    --fast        Skip slow integration tests
    --html        Generate HTML coverage report
    --pytest      Use pytest instead of unittest
"""

import sys
import os
import unittest
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Optional dependencies
try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


def simple_test_run():
    """Simple test runner function (original functionality)."""
    print("=" * 60)
    print("UVI (Unified Verb Index) - Test Suite")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    print("\nRunning UVI tests...\n")
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] ALL TESTS PASSED")
        print("The UVI package is functioning correctly!")
    else:
        print("\n[FAILED] SOME TESTS FAILED")
        print("Please review the test output above.")
    
    print("=" * 60)
    
    return result.wasSuccessful()


class UVITestRunner:
    """Comprehensive test runner for UVI package."""
    
    def __init__(self):
        """Initialize test runner."""
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.coverage_enabled = False
        self.cov = None
        
    def setup_coverage(self, html_output: bool = False):
        """Set up coverage analysis."""
        if not COVERAGE_AVAILABLE:
            print("Warning: coverage package not available. Install with: pip install coverage")
            return False
        
        self.cov = coverage.Coverage(
            source=['src/uvi'],
            omit=[
                '*/tests/*',
                '*/test_*',
                '*/venv/*',
                '*/.venv/*'
            ]
        )
        self.cov.start()
        self.coverage_enabled = True
        self.html_output = html_output
        return True
    
    def discover_tests(self, pattern: str = 'test_*.py') -> unittest.TestSuite:
        """Discover tests in the test directory."""
        loader = unittest.TestLoader()
        return loader.discover(str(self.test_dir), pattern=pattern)
    
    def run_test_suite(self, suite: unittest.TestSuite, verbose: bool = False) -> Dict[str, Any]:
        """Run a test suite and return results."""
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            stream=sys.stdout,
            buffer=True
        )
        
        start_time = time.time()
        result = runner.run(suite)
        duration = time.time() - start_time
        
        return {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1) * 100,
            'duration': duration,
            'result': result
        }
    
    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run unit tests."""
        print("=" * 60)
        print("RUNNING UNIT TESTS")
        print("=" * 60)
        
        # Discover unit tests (excluding integration tests)
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Load specific unit test files
        for test_file in ['test_uvi.py', 'test_parsers.py', 'test_utils.py', 'test_new_classes.py']:
            test_path = self.test_dir / test_file
            if test_path.exists():
                try:
                    module_tests = loader.discover(str(self.test_dir), pattern=test_file)
                    suite.addTests(module_tests)
                except Exception as e:
                    print(f"Warning: Could not load {test_file}: {e}")
        
        result = self.run_test_suite(suite, verbose)
        result['type'] = 'unit'
        return result
    
    def run_integration_tests(self, verbose: bool = False, fast: bool = False) -> Dict[str, Any]:
        """Run integration tests."""
        print("\n" + "=" * 60)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 60)
        
        # Load integration tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        for test_file in ['test_integration.py', 'test_corpus_loader.py']:
            test_path = self.test_dir / test_file
            if test_path.exists():
                try:
                    module_tests = loader.discover(str(self.test_dir), pattern=test_file)
                    suite.addTests(module_tests)
                except Exception as e:
                    print(f"Warning: Could not load {test_file}: {e}")
        
        result = self.run_test_suite(suite, verbose)
        result['type'] = 'integration'
        return result
    
    def run_all_tests(self, verbose: bool = False, fast: bool = False) -> Dict[str, Any]:
        """Run all tests."""
        print("Starting UVI Package Test Suite")
        print("=" * 60)
        
        all_results = []
        
        # Run unit tests
        unit_results = self.run_unit_tests(verbose)
        all_results.append(unit_results)
        
        # Run integration tests
        integration_results = self.run_integration_tests(verbose, fast)
        all_results.append(integration_results)
        
        return self.summarize_results(all_results)
    
    def summarize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize test results."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        total_duration = 0
        
        for result in results:
            test_type = result['type'].title()
            tests_run = result['tests_run']
            failures = result['failures']
            errors = result['errors']
            skipped = result['skipped']
            success_rate = result['success_rate']
            duration = result['duration']
            
            print(f"\n{test_type} Tests:")
            print(f"  Tests run: {tests_run}")
            print(f"  Failures:  {failures}")
            print(f"  Errors:    {errors}")
            print(f"  Skipped:   {skipped}")
            print(f"  Success:   {success_rate:.1f}%")
            print(f"  Duration:  {duration:.2f}s")
            
            total_tests += tests_run
            total_failures += failures
            total_errors += errors
            total_skipped += skipped
            total_duration += duration
        
        overall_success_rate = (total_tests - total_failures - total_errors) / max(total_tests, 1) * 100
        
        print(f"\nOVERALL RESULTS:")
        print(f"  Total tests: {total_tests}")
        print(f"  Failures:    {total_failures}")
        print(f"  Errors:      {total_errors}")
        print(f"  Skipped:     {total_skipped}")
        print(f"  Success:     {overall_success_rate:.1f}%")
        print(f"  Duration:    {total_duration:.2f}s")
        
        if overall_success_rate == 100:
            print("\n[SUCCESS] ALL TESTS PASSED")
            print("The UVI package is functioning correctly!")
        else:
            print("\n[FAILED] SOME TESTS FAILED")
            print("Please review the test output above.")
        
        print("=" * 60)
        
        return {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'total_skipped': total_skipped,
            'overall_success_rate': overall_success_rate,
            'total_duration': total_duration,
            'individual_results': results
        }
    
    def generate_coverage_report(self):
        """Generate coverage report."""
        if not self.coverage_enabled or not self.cov:
            return
        
        self.cov.stop()
        self.cov.save()
        
        print("\n" + "=" * 60)
        print("COVERAGE ANALYSIS")
        print("=" * 60)
        
        # Print coverage report to stdout
        self.cov.report(show_missing=True)
        
        # Generate HTML report if requested
        if hasattr(self, 'html_output') and self.html_output:
            html_dir = self.project_root / 'coverage_html'
            print(f"\nGenerating HTML coverage report in: {html_dir}")
            self.cov.html_report(directory=str(html_dir))
    
    def run_with_pytest(self, test_type: str = 'all', verbose: bool = False, coverage: bool = False):
        """Run tests using pytest if available."""
        if not PYTEST_AVAILABLE:
            print("pytest not available. Install with: pip install pytest")
            return False
        
        import subprocess
        
        cmd = ['python', '-m', 'pytest']
        
        if coverage and COVERAGE_AVAILABLE:
            cmd.extend(['--cov=uvi', '--cov-report=term-missing'])
        
        if verbose:
            cmd.append('-v')
        
        # Add test directory
        cmd.append(str(self.test_dir))
        
        print("Running tests with pytest:")
        print(" ".join(cmd))
        print()
        
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            return result.returncode == 0
        except Exception as e:
            print(f"Error running pytest: {e}")
            return False


def main():
    """Main test runner function."""
    # If no arguments provided, run simple test
    if len(sys.argv) == 1:
        success = simple_test_run()
        sys.exit(0 if success else 1)
    
    # Parse advanced options
    parser = argparse.ArgumentParser(description="UVI Package Test Runner")
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage analysis')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Run tests with verbose output')
    parser.add_argument('--integration', action='store_true',
                       help='Run only integration tests')
    parser.add_argument('--unit', action='store_true',
                       help='Run only unit tests')
    parser.add_argument('--fast', action='store_true',
                       help='Skip slow integration tests')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML coverage report')
    parser.add_argument('--pytest', action='store_true',
                       help='Use pytest instead of unittest')
    
    args = parser.parse_args()
    
    runner = UVITestRunner()
    
    # Use pytest if requested and available
    if args.pytest:
        test_type = 'unit' if args.unit else 'integration' if args.integration else 'all'
        success = runner.run_with_pytest(test_type, args.verbose, args.coverage)
        sys.exit(0 if success else 1)
    
    # Set up coverage if requested
    if args.coverage:
        if not runner.setup_coverage(args.html):
            print("Coverage analysis not available")
            args.coverage = False
    
    # Run tests
    try:
        if args.unit:
            results = runner.run_unit_tests(args.verbose)
        elif args.integration:
            results = runner.run_integration_tests(args.verbose, args.fast)
        else:
            results = runner.run_all_tests(args.verbose, args.fast)
        
        # Generate coverage report if enabled
        if args.coverage:
            runner.generate_coverage_report()
        
        # Exit with appropriate code
        if isinstance(results, dict):
            failures = results.get('total_failures', 0)
            errors = results.get('total_errors', 0)
            sys.exit(0 if failures == 0 and errors == 0 else 1)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()