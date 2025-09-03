"""
Shared pytest fixtures and configuration.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_repo(temp_dir: Path) -> Path:
    """Create a sample repository structure for testing."""
    # Create directory structure
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "docs").mkdir()
    (temp_dir / ".git").mkdir()
    
    # Create sample Python files
    main_py = temp_dir / "main.py"
    main_py.write_text('''#!/usr/bin/env python3
"""Main application entry point."""

def main():
    """Run the application."""
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    exit(main())
''')
    
    # Create source files
    core_py = temp_dir / "src" / "core.py"
    core_py.write_text('''"""Core functionality."""

class Calculator:
    """A simple calculator class."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

def process_data(data: list) -> dict:
    """Process input data."""
    return {"count": len(data), "data": data}
''')
    
    utils_py = temp_dir / "src" / "utils.py"
    utils_py.write_text('''"""Utility functions."""

def format_string(s: str) -> str:
    """Format a string."""
    return s.strip().lower()

def validate_input(value: any) -> bool:
    """Validate input value."""
    return value is not None
''')
    
    # Create test file
    test_core = temp_dir / "tests" / "test_core.py"
    test_core.write_text('''"""Tests for core module."""
import pytest
from src.core import Calculator

def test_calculator_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_calculator_multiply():
    calc = Calculator()
    assert calc.multiply(3, 4) == 12
''')
    
    # Create documentation
    readme = temp_dir / "README.md"
    readme.write_text('''# Sample Project

This is a sample project for testing src2md.

## Features
- Calculator functionality
- Data processing
- Utility functions

## Installation
```bash
pip install -e .
```
''')
    
    # Create config files
    gitignore = temp_dir / ".gitignore"
    gitignore.write_text('''__pycache__/
*.pyc
.env
.venv/
''')
    
    setup_py = temp_dir / "setup.py"
    setup_py.write_text('''from setuptools import setup, find_packages

setup(
    name="sample-project",
    version="0.1.0",
    packages=find_packages(),
)
''')
    
    return temp_dir


@pytest.fixture
def sample_python_content() -> str:
    """Sample Python file content for testing."""
    return '''"""Sample module for testing."""
import os
import sys
from typing import List, Dict, Optional

class SampleClass:
    """A sample class with various methods."""
    
    def __init__(self, name: str):
        """Initialize with name."""
        self.name = name
        self._private_var = 42
    
    def public_method(self, value: int) -> int:
        """A public method that doubles the input."""
        return value * 2
    
    def _private_method(self) -> None:
        """A private method."""
        pass

def exported_function(data: List[str]) -> Dict[str, int]:
    """Process a list of strings."""
    result = {}
    for item in data:
        if item:
            result[item] = len(item)
    return result

def _internal_function():
    """Internal function not meant for export."""
    pass

if __name__ == "__main__":
    # Main execution
    obj = SampleClass("test")
    print(obj.public_method(5))
'''


@pytest.fixture
def sample_javascript_content() -> str:
    """Sample JavaScript file content for testing."""
    return '''// Sample JavaScript module
import { useState, useEffect } from 'react';
import axios from 'axios';

export class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async fetchData(endpoint) {
        try {
            const response = await axios.get(`${this.baseUrl}/${endpoint}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching data:', error);
            throw error;
        }
    }
}

export function processData(items) {
    return items.map(item => ({
        ...item,
        processed: true
    }));
}

export const API_VERSION = '1.0.0';

const internalHelper = () => {
    // Internal function
};
'''