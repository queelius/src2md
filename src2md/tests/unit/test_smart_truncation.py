"""
Unit tests for smart truncation in context optimization.
"""
import pytest
from src2md.core.context import ContextOptimizer, ContextWindow, TokenCounter


class TestSmartTruncation:
    """Test smart truncation functionality."""
    
    @pytest.fixture
    def sample_code(self):
        """Sample Python code for testing."""
        return '''"""
Module docstring for testing.
"""
import os
import sys
from typing import List, Dict

def helper_function():
    """A helper function."""
    return 42

class MainClass:
    """Main class with several methods."""
    
    def __init__(self):
        self.data = []
    
    def method_one(self, param: str) -> str:
        """First method with documentation."""
        result = param.upper()
        # Some processing
        for i in range(10):
            result += str(i)
        return result
    
    def method_two(self, items: List[Dict]) -> List:
        """Second method that processes items."""
        output = []
        for item in items:
            if item.get('valid'):
                processed = self._process_item(item)
                output.append(processed)
        return output
    
    def _process_item(self, item: Dict) -> Dict:
        """Private method for processing."""
        return {k: v for k, v in item.items() if v}

def main():
    """Main entry point."""
    instance = MainClass()
    result = instance.method_one("test")
    print(result)
    
    items = [{'valid': True, 'data': 'test'}]
    processed = instance.method_two(items)
    print(processed)

if __name__ == "__main__":
    main()
'''
    
    def test_preserve_structure(self, sample_code):
        """Test that smart truncation preserves code structure."""
        optimizer = ContextOptimizer(ContextWindow.CUSTOM)
        optimizer.limit = 1000  # Small limit to force truncation
        
        truncated = optimizer.optimize_content(
            sample_code, 
            target_tokens=100,
            preserve_structure=True
        )
        
        # Should preserve imports
        assert "import os" in truncated or "import" in truncated
        
        # Should have some structure preserved
        assert "class" in truncated or "def" in truncated
        
        # Should be shorter than original
        assert len(truncated) < len(sample_code)
    
    def test_no_preserve_structure(self, sample_code):
        """Test simple truncation without structure preservation."""
        optimizer = ContextOptimizer(ContextWindow.CUSTOM)
        optimizer.limit = 1000
        
        truncated = optimizer.optimize_content(
            sample_code,
            target_tokens=50,
            preserve_structure=False
        )
        
        # Should be truncated to approximately target tokens
        token_count = TokenCounter.count(truncated)
        assert token_count <= 50
    
    def test_imports_preserved(self):
        """Test that imports are prioritized in smart truncation."""
        code = '''import numpy as np
import pandas as pd
from sklearn import model_selection
import tensorflow as tf

def very_long_function():
    """ This is a very long function with lots of code """
    x = 1
    y = 2
    z = 3
    # ... imagine hundreds of lines here
    return x + y + z
''' + '\n'.join(['    # more code'] * 100)
        
        optimizer = ContextOptimizer.with_limit(100)
        truncated = optimizer.optimize_content(
            code,
            target_tokens=50,
            preserve_structure=True
        )
        
        # Imports should be preserved even with aggressive truncation
        assert "import" in truncated
    
    def test_module_docstring_preserved(self):
        """Test that module docstrings are preserved."""
        code = '''"""
This is an important module docstring that explains
what this module does and how to use it.
"""

import os

''' + 'x = 1\n' * 100  # Lots of code
        
        optimizer = ContextOptimizer.with_limit(200)
        truncated = optimizer.optimize_content(
            code,
            target_tokens=60,
            preserve_structure=True
        )
        
        # Module docstring should be preserved
        assert '"""' in truncated
    
    def test_function_signatures_preserved(self):
        """Test that function signatures are preserved over bodies."""
        code = '''
def important_function(param1: str, param2: int) -> Dict:
    """This function does important things."""
    # Lots of implementation details
    result = {}
    for i in range(100):
        result[str(i)] = i * 2
    return result

def another_function(data: List) -> None:
    """Another important function."""
    # More implementation
    for item in data:
        process(item)
'''
        
        optimizer = ContextOptimizer.with_limit(100)
        truncated = optimizer._smart_truncate(code, 30)
        
        # Should preserve function signatures
        assert "def important_function" in truncated or "def another_function" in truncated
    
    def test_class_structure_preserved(self):
        """Test that class structure is maintained."""
        code = '''
class MyClass:
    """A test class."""
    
    def __init__(self, value):
        self.value = value
        self.data = []
        # Lots of initialization code
        for i in range(100):
            self.data.append(i)
    
    def method_one(self):
        """First method."""
        return self.value * 2
    
    def method_two(self):
        """Second method."""
        return sum(self.data)
'''
        
        optimizer = ContextOptimizer.with_limit(100)
        truncated = optimizer._smart_truncate(code, 40)
        
        # Should preserve class definition
        assert "class MyClass" in truncated
        # Should have some indication of methods
        assert "def " in truncated or "..." in truncated
    
    def test_summarize_unit(self):
        """Test unit summarization helper."""
        optimizer = ContextOptimizer.with_limit(100)
        
        # Test function summarization
        func_lines = [
            "def my_function(param1, param2):",
            "    '''Docstring'''",
            "    result = param1 + param2",
            "    return result"
        ]
        
        summary = optimizer._summarize_unit(func_lines)
        assert "def my_function(param1, param2):" in summary
        assert "..." in summary
        
        # Test class summarization
        class_lines = [
            "class MyClass:",
            "    def __init__(self):",
            "        pass"
        ]
        
        summary = optimizer._summarize_unit(class_lines)
        assert "class MyClass:" in summary
        assert "..." in summary
    
    def test_edge_cases(self):
        """Test edge cases in smart truncation."""
        optimizer = ContextOptimizer.with_limit(100)
        
        # Empty content
        assert optimizer._smart_truncate("", 10) == ""
        
        # Very short content
        short = "def f(): pass"
        assert optimizer._smart_truncate(short, 100) == short
        
        # Content already within limit
        content = "import os\ndef func(): pass"
        tokens = TokenCounter.count(content)
        if tokens <= 50:
            assert optimizer._smart_truncate(content, 50) == content