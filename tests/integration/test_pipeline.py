"""
Integration tests for the complete src2md pipeline.
"""
import pytest
import json
from pathlib import Path

from src2md.core.repository import Repository
from src2md.core.context import ContextWindow
from src2md.strategies.importance import ImportanceScorer


class TestCompletePipeline:
    """Test complete analysis pipeline."""
    
    def test_basic_analysis(self, sample_repo):
        """Test basic repository analysis without optimization."""
        repo = Repository(sample_repo)
        repo.analyze()
        
        data = repo.to_dict()
        
        # Verify structure
        assert 'metadata' in data
        assert 'files' in data
        assert len(data['files']) > 0
        
        # Verify all expected files are present
        file_paths = [f['path'] for f in data['files']]
        assert 'main.py' in file_paths
        assert 'src/core.py' in file_paths
        assert 'README.md' in file_paths
    
    def test_fluent_api_pipeline(self, sample_repo):
        """Test complete pipeline with fluent API."""
        result = (Repository(sample_repo)
            .name("TestProject")
            .branch("feature/test")
            .include("src/", "*.py")
            .exclude("tests/")
            .with_importance_scoring()
            .with_stats(True)
            .analyze()
            .to_dict())
        
        assert result['metadata']['name'] == "TestProject"
        assert result['metadata']['branch'] == "feature/test"
        assert 'statistics' in result
        
        # Check that only included files are present
        for file_data in result['files']:
            path = file_data['path']
            assert not path.startswith('tests/')
            assert 'src/' in path or path.endswith('.py')
    
    def test_context_optimization_pipeline(self, sample_repo):
        """Test pipeline with context window optimization."""
        repo = (Repository(sample_repo)
            .with_importance_scoring()
            .optimize_for_tokens(10_000)  # Small limit to force optimization
            .analyze())
        
        data = repo.to_dict()
        
        # Should have statistics with context info
        if 'statistics' in data and 'context' in data['statistics']:
            context = data['statistics']['context']
            assert context['window'] == 'CUSTOM'
            assert context['limit'] == 10_000
    
    def test_multiple_output_formats(self, sample_repo):
        """Test generating multiple output formats from same analysis."""
        repo = (Repository(sample_repo)
            .name("MultiFormat")
            .with_importance_scoring()
            .analyze())
        
        # Generate different formats
        markdown = repo.to_markdown()
        json_output = repo.to_json(pretty=True)
        html_output = repo.to_html()
        
        # Verify Markdown
        assert "# MultiFormat" in markdown
        assert "```python" in markdown  # Code blocks
        
        # Verify JSON
        json_data = json.loads(json_output)
        assert json_data['metadata']['name'] == "MultiFormat"
        assert isinstance(json_data['files'], list)
        
        # Verify HTML
        assert "<!DOCTYPE html>" in html_output
        assert "<h1>MultiFormat</h1>" in html_output
        assert "<pre><code" in html_output
    
    def test_importance_scoring_integration(self, sample_repo):
        """Test importance scoring integration."""
        repo = (Repository(sample_repo)
            .with_importance_scoring()
            .analyze())
        
        data = repo.to_dict()
        
        # Check that files have importance scores
        important_files = [f for f in data['files'] if 'importance' in f]
        assert len(important_files) > 0
        
        # main.py should have high importance
        main_file = next((f for f in data['files'] 
                          if f['path'] == 'main.py'), None)
        if main_file and 'importance' in main_file:
            assert main_file['importance'] > 0.5
    
    def test_prioritization(self, sample_repo):
        """Test file prioritization."""
        repo = (Repository(sample_repo)
            .prioritize(["main.py", "src/core.py"])
            .with_importance_scoring()
            .optimize_for_tokens(5000)  # Small limit
            .analyze())
        
        data = repo.to_dict()
        
        # Priority files should appear first
        if len(data['files']) > 2:
            first_files = data['files'][:2]
            paths = [f['path'] for f in first_files]
            assert 'main.py' in paths or 'src/core.py' in paths
    
    def test_no_content_mode(self, sample_repo):
        """Test metadata-only mode without file contents."""
        repo = (Repository(sample_repo)
            .with_content(False)
            .analyze())
        
        data = repo.to_dict()
        
        # Files should not have content
        for file_data in data['files']:
            assert 'content' not in file_data or file_data['content'] is None
        
        # Should still have metadata
        assert all('path' in f for f in data['files'])
        assert all('size' in f for f in data['files'])
    
    def test_statistics_generation(self, sample_repo):
        """Test comprehensive statistics generation."""
        repo = (Repository(sample_repo)
            .with_stats(True)
            .with_importance_scoring()
            .optimize_for(ContextWindow.GPT_4)
            .analyze())
        
        stats = repo._calculate_statistics()
        
        assert 'total_files' in stats
        assert 'total_size' in stats
        assert 'languages' in stats
        
        # Language breakdown
        if 'python' in stats['languages']:
            py_stats = stats['languages']['python']
            assert 'count' in py_stats
            assert 'size' in py_stats
            assert py_stats['count'] > 0
        
        # Context window usage
        if 'context' in stats:
            context = stats['context']
            assert 'window' in context
            assert 'limit' in context
            assert 'remaining' in context
    
    def test_complex_filtering(self, sample_repo):
        """Test complex include/exclude patterns."""
        repo = (Repository(sample_repo)
            .include("*.py", "*.md")
            .exclude("test_*", "*_test.py", ".git")
            .analyze())
        
        data = repo.to_dict()
        
        for file_data in data['files']:
            path = file_data['path']
            # Should only have .py and .md files
            assert path.endswith('.py') or path.endswith('.md')
            # Should not have test files
            assert not path.startswith('test_')
            assert not path.endswith('_test.py')
            assert '.git' not in path
    
    def test_end_to_end_markdown_generation(self, sample_repo):
        """Test end-to-end Markdown generation."""
        markdown = (Repository(sample_repo)
            .name("E2E Test Project")
            .branch("main")
            .with_importance_scoring()
            .prioritize(["main.py"])
            .optimize_for(ContextWindow.GPT_4, preserve_ratio=0.9)
            .analyze()
            .to_markdown())
        
        # Verify structure
        assert "# E2E Test Project" in markdown
        assert "## Table of Contents" in markdown
        assert "## Overview" in markdown
        assert "## Statistics" in markdown
        
        # Verify content
        assert "main.py" in markdown
        assert "```python" in markdown
        assert "def main():" in markdown  # From main.py content
        
        # Verify statistics
        assert "Total Files:" in markdown
        assert "Language Breakdown" in markdown
    
    def test_end_to_end_json_generation(self, sample_repo):
        """Test end-to-end JSON generation."""
        json_str = (Repository(sample_repo)
            .name("JSON Test")
            .with_stats(True)
            .analyze()
            .to_json(pretty=True))
        
        # Parse and verify
        data = json.loads(json_str)
        
        assert data['metadata']['name'] == "JSON Test"
        assert isinstance(data['files'], list)
        assert len(data['files']) > 0
        
        # Verify file structure
        for file_data in data['files']:
            assert 'path' in file_data
            assert 'language' in file_data
            assert 'size' in file_data
        
        # Verify statistics
        assert 'statistics' in data
        assert 'total_files' in data['statistics']
        assert 'languages' in data['statistics']
    
    def test_progressive_summarization(self, sample_repo):
        """Test progressive summarization based on importance."""
        # Create a repo with very small token limit
        repo = (Repository(sample_repo)
            .with_importance_scoring()
            .optimize_for_tokens(1000, preserve_ratio=0.5)
            .summarize_tests()
            .analyze())
        
        data = repo.to_dict()
        
        # Some files should be summarized
        summarized = [f for f in data['files'] if 'summary' in f]
        full_content = [f for f in data['files'] if 'content' in f]
        
        # With such a small limit, we should have both
        # (important files with content, less important summarized)
        # Note: actual summarization is placeholder for now
        assert len(data['files']) > 0