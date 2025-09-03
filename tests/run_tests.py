#!/usr/bin/env python3
"""
Test runner script for src2md.
"""
import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with coverage."""
    root_dir = Path(__file__).parent.parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--cov=src2md",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ]
    
    print("Running tests with coverage...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd, cwd=root_dir)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed")
        sys.exit(1)


def run_unit_tests():
    """Run only unit tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "-m", "unit",
        "tests/unit/"
    ]
    
    print("Running unit tests...")
    subprocess.run(cmd)


def run_integration_tests():
    """Run only integration tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "-m", "integration",
        "tests/integration/"
    ]
    
    print("Running integration tests...")
    subprocess.run(cmd)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run src2md tests")
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true", 
        help="Run only integration tests"
    )
    
    args = parser.parse_args()
    
    if args.unit:
        run_unit_tests()
    elif args.integration:
        run_integration_tests()
    else:
        run_tests()