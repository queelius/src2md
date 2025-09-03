"""
Unit tests for output formatters.
"""
import pytest
import json
from src2md.formatters.base import Formatter, StreamingFormatter
from src2md.formatters.markdown import MarkdownFormatter
from src2md.formatters.json import JSONFormatter, JSONLFormatter
from src2md.formatters.html import HTMLFormatter


class TestBaseFormatter:
    """Test base Formatter class."""
    
    def test_initialization(self):
        """Test formatter initialization with options."""
        class TestFormatter(Formatter):
            def format(self, data):
                return "test"
        
        formatter = TestFormatter(option1="value1", option2=42)
        assert formatter.options == {"option1": "value1", "option2": 42}
    
    def test_validate_data_valid(self):
        """Test data validation with valid data."""
        class TestFormatter(Formatter):
            def format(self, data):
                return "test"
        
        formatter = TestFormatter()
        data = {"metadata": {}, "files": []}
        
        assert formatter.validate_data(data) is True
    
    def test_validate_data_missing_keys(self):
        """Test data validation with missing keys."""
        class TestFormatter(Formatter):
            def format(self, data):
                return "test"
        
        formatter = TestFormatter()
        
        with pytest.raises(ValueError, match="Missing required key: metadata"):
            formatter.validate_data({"files": []})
        
        with pytest.raises(ValueError, match="Missing required key: files"):
            formatter.validate_data({"metadata": {}})
    
    def test_validate_data_wrong_type(self):
        """Test data validation with wrong types."""
        class TestFormatter(Formatter):
            def format(self, data):
                return "test"
        
        formatter = TestFormatter()
        
        with pytest.raises(ValueError, match="'files' must be a list"):
            formatter.validate_data({"metadata": {}, "files": "not a list"})
    
    def test_get_option(self):
        """Test getting formatter options."""
        class TestFormatter(Formatter):
            def format(self, data):
                return "test"
        
        formatter = TestFormatter(option1="value1")
        
        assert formatter.get_option("option1") == "value1"
        assert formatter.get_option("nonexistent") is None
        assert formatter.get_option("nonexistent", "default") == "default"


class TestMarkdownFormatter:
    """Test MarkdownFormatter class."""
    
    def test_initialization(self):
        """Test Markdown formatter initialization."""
        formatter = MarkdownFormatter(include_toc=False, include_stats=False)
        assert formatter.include_toc is False
        assert formatter.include_stats is False
    
    def test_format_header(self):
        """Test header formatting."""
        formatter = MarkdownFormatter()
        metadata = {
            "name": "TestProject",
            "path": "/test/path",
            "branch": "main",
            "file_count": 10
        }
        
        header = formatter.format_header(metadata)
        
        assert "# TestProject" in header
        assert "**Path:** `/test/path`" in header
        assert "**Branch:** `main`" in header
        assert "10 analyzed files" in header
    
    def test_format_file(self):
        """Test file formatting."""
        formatter = MarkdownFormatter()
        file_data = {
            "path": "src/main.py",
            "language": "python",
            "size": 1024,
            "importance": 0.85,
            "content": "print('hello')"
        }
        
        output = formatter.format_file(file_data)
        
        assert "### `src/main.py`" in output
        assert "Language: python" in output
        assert "Size: 1.0 KB" in output
        assert "Importance: 0.85" in output
        assert "```python" in output
        assert "print('hello')" in output
    
    def test_format_file_with_summary(self):
        """Test file formatting with summary instead of content."""
        formatter = MarkdownFormatter()
        file_data = {
            "path": "src/main.py",
            "summary": "This file contains the main entry point"
        }
        
        output = formatter.format_file(file_data)
        
        assert "### `src/main.py`" in output
        assert "This file contains the main entry point" in output
        assert "```" not in output  # No code block
    
    def test_format_footer_with_statistics(self):
        """Test footer formatting with statistics."""
        formatter = MarkdownFormatter()
        statistics = {
            "total_files": 25,
            "total_size": 51200,
            "languages": {
                "python": {"count": 15, "size": 30000},
                "javascript": {"count": 10, "size": 21200}
            },
            "context": {
                "window": "GPT_4",
                "limit": 128000,
                "used": 45000,
                "utilization": 0.35
            }
        }
        
        footer = formatter.format_footer(statistics)
        
        assert "## Statistics" in footer
        assert "**Total Files:** 25" in footer
        assert "**Total Size:** 50.0 KB" in footer
        assert "### Language Breakdown" in footer
        assert "| python |" in footer
        assert "| javascript |" in footer
        assert "### Context Window Usage" in footer
        assert "**Window Type:** GPT_4" in footer
        assert "**Token Limit:** 128,000" in footer
    
    def test_format_size(self):
        """Test size formatting."""
        formatter = MarkdownFormatter()
        
        assert formatter._format_size(512) == "512.0 B"
        assert formatter._format_size(1024) == "1.0 KB"
        assert formatter._format_size(1024 * 1024) == "1.0 MB"
        assert formatter._format_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_format_complete(self):
        """Test complete document formatting."""
        formatter = MarkdownFormatter()
        data = {
            "metadata": {"name": "Test", "file_count": 2},
            "files": [
                {"path": "file1.py", "language": "python", "content": "code1"},
                {"path": "file2.js", "language": "javascript", "content": "code2"}
            ],
            "statistics": {"total_files": 2, "total_size": 100}
        }
        
        output = formatter.format(data)
        
        assert "# Test" in output
        assert "file1.py" in output
        assert "file2.js" in output
        assert "## Statistics" in output


class TestJSONFormatter:
    """Test JSONFormatter class."""
    
    def test_initialization(self):
        """Test JSON formatter initialization."""
        formatter = JSONFormatter(pretty=False, indent=4)
        assert formatter.pretty is False
        assert formatter.indent is None  # Should be None when pretty=False
    
    def test_format_pretty(self):
        """Test pretty JSON formatting."""
        formatter = JSONFormatter(pretty=True, indent=2)
        data = {
            "metadata": {"name": "Test"},
            "files": [{"path": "file.py", "content": "code"}]
        }
        
        output = formatter.format(data)
        parsed = json.loads(output)
        
        assert parsed == data
        assert "\n" in output  # Pretty formatting includes newlines
        assert "  " in output  # Indentation
    
    def test_format_compact(self):
        """Test compact JSON formatting."""
        formatter = JSONFormatter(pretty=False)
        data = {
            "metadata": {"name": "Test"},
            "files": [{"path": "file.py", "content": "code"}]
        }
        
        output = formatter.format(data)
        parsed = json.loads(output)
        
        assert parsed == data
        assert output.count("\n") == 0  # Compact format, no newlines


class TestJSONLFormatter:
    """Test JSONLFormatter class."""
    
    def test_format(self):
        """Test JSONL formatting."""
        formatter = JSONLFormatter()
        data = {
            "metadata": {"name": "Test", "version": "1.0"},
            "statistics": {"total_files": 2},
            "files": [
                {"path": "file1.py", "content": "code1"},
                {"path": "file2.js", "content": "code2"}
            ]
        }
        
        output = formatter.format(data)
        lines = output.strip().split("\n")
        
        # Should have 4 lines: metadata, statistics, 2 files
        assert len(lines) == 4
        
        # Parse each line
        line1 = json.loads(lines[0])
        assert line1["type"] == "metadata"
        assert line1["data"]["name"] == "Test"
        
        line2 = json.loads(lines[1])
        assert line2["type"] == "statistics"
        assert line2["data"]["total_files"] == 2
        
        line3 = json.loads(lines[2])
        assert line3["type"] == "file"
        assert line3["data"]["path"] == "file1.py"
        
        line4 = json.loads(lines[3])
        assert line4["type"] == "file"
        assert line4["data"]["path"] == "file2.js"


class TestHTMLFormatter:
    """Test HTMLFormatter class."""
    
    def test_initialization(self):
        """Test HTML formatter initialization."""
        formatter = HTMLFormatter(include_styles=False)
        assert formatter.include_styles is False
    
    def test_format_header(self):
        """Test HTML header formatting."""
        formatter = HTMLFormatter()
        metadata = {
            "name": "TestProject",
            "path": "/test/path",
            "branch": "main"
        }
        
        header = formatter.format_header(metadata)
        
        assert "<h1>TestProject</h1>" in header
        assert "<strong>Path:</strong>" in header
        assert "<code>/test/path</code>" in header
        assert "<strong>Branch:</strong>" in header
        assert "<code>main</code>" in header
    
    def test_format_file(self):
        """Test HTML file formatting."""
        formatter = HTMLFormatter()
        file_data = {
            "path": "src/main.py",
            "language": "python",
            "size": 1024,
            "content": "<script>alert('xss')</script>"
        }
        
        output = formatter.format_file(file_data)
        
        assert '<code>src/main.py</code>' in output
        assert 'Language: python' in output
        assert 'Size: 1.0 KB' in output
        # Content should be escaped
        assert '&lt;script&gt;' in output
        assert '<script>' not in output  # Should be escaped
    
    def test_format_complete_document(self):
        """Test complete HTML document generation."""
        formatter = HTMLFormatter(include_styles=True)
        data = {
            "metadata": {"name": "Test"},
            "files": [{"path": "file.py", "content": "print('hello')"}],
            "statistics": {"total_files": 1}
        }
        
        output = formatter.format(data)
        
        assert "<!DOCTYPE html>" in output
        assert "<html" in output
        assert "</html>" in output
        assert "<head>" in output
        assert "<body>" in output
        assert "<style>" in output  # Styles included
        assert "<h1>Test</h1>" in output
    
    def test_get_styles(self):
        """Test CSS styles generation."""
        formatter = HTMLFormatter()
        styles = formatter._get_styles()
        
        assert "<style>" in styles
        assert "body {" in styles
        assert "font-family:" in styles
        assert ".container {" in styles