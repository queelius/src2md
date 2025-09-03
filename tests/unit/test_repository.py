"""
Unit tests for Repository class with fluent API.
"""
import pytest
from pathlib import Path

from src2md.core.repository import Repository, FileEntry
from src2md.core.context import ContextWindow
from src2md.strategies.importance import ImportanceScorer


class TestFileEntry:
    """Test FileEntry dataclass."""
    
    def test_initialization(self):
        """Test FileEntry initialization."""
        entry = FileEntry(
            path=Path("/test/file.py"),
            relative_path=Path("file.py"),
            content="print('hello')",
            size=14,
            language="python"
        )
        
        assert entry.path == Path("/test/file.py")
        assert entry.relative_path == Path("file.py")
        assert entry.content == "print('hello')"
        assert entry.size == 14
        assert entry.language == "python"
        assert entry.importance is None
        assert entry.summary is None
        assert entry.metadata == {}


class TestRepository:
    """Test Repository class."""
    
    def test_initialization_with_valid_path(self, sample_repo):
        """Test repository initialization with valid directory."""
        repo = Repository(sample_repo)
        assert repo.path == sample_repo
        assert repo._name == sample_repo.name
        assert repo._analyzed is False
    
    def test_initialization_with_invalid_path(self):
        """Test repository initialization with invalid path."""
        with pytest.raises(ValueError, match="does not exist"):
            Repository("/nonexistent/path")
    
    def test_initialization_with_file_path(self, temp_dir):
        """Test repository initialization with file instead of directory."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("content")
        
        with pytest.raises(ValueError, match="not a directory"):
            Repository(file_path)
    
    def test_fluent_api_methods(self, sample_repo):
        """Test fluent API method chaining."""
        repo = Repository(sample_repo)
        
        # Test chaining
        result = (repo
            .name("TestProject")
            .branch("main")
            .include("src/")
            .exclude("tests/")
            .with_importance_scoring()
            .with_dependency_graph()
            .with_content(True)
            .with_stats(True))
        
        assert result is repo  # Methods should return self
        assert repo._name == "TestProject"
        assert repo._branch == "main"
        assert "src/" in repo._include_patterns
        assert "tests/" in repo._exclude_patterns
        assert repo._importance_scorer is not None
        assert repo._config['include_dependencies'] is True
        assert repo._config['include_content'] is True
        assert repo._config['include_stats'] is True
    
    def test_optimize_for_window(self, sample_repo):
        """Test optimization for context window."""
        repo = Repository(sample_repo)
        
        result = repo.optimize_for(ContextWindow.GPT_4, preserve_ratio=0.9)
        
        assert result is repo
        assert repo._context_optimizer is not None
        assert repo._config['preserve_ratio'] == 0.9
    
    def test_optimize_for_tokens(self, sample_repo):
        """Test optimization for token limit."""
        repo = Repository(sample_repo)
        
        result = repo.optimize_for_tokens(50_000, preserve_ratio=0.8)
        
        assert result is repo
        assert repo._context_optimizer is not None
        assert repo._context_optimizer.limit == 50_000
        assert repo._config['preserve_ratio'] == 0.8
    
    def test_prioritize(self, sample_repo):
        """Test path prioritization."""
        repo = Repository(sample_repo)
        
        result = repo.prioritize(["src/core/", "main.py"])
        
        assert result is repo
        assert repo._metadata['priority_paths'] == ["src/core/", "main.py"]
    
    def test_summarization_settings(self, sample_repo):
        """Test summarization settings."""
        repo = Repository(sample_repo)
        
        result = repo.summarize_tests().summarize_docs()
        
        assert result is repo
        assert repo._metadata['summarize_tests'] is True
        assert repo._metadata['summarize_docs'] is True
    
    def test_collect_files(self, sample_repo):
        """Test file collection."""
        repo = Repository(sample_repo)
        repo._collect_files()
        
        assert len(repo._files) > 0
        
        # Check that files were collected
        file_paths = [str(f.relative_path) for f in repo._files]
        assert "main.py" in file_paths
        assert "src/core.py" in file_paths
        assert "src/utils.py" in file_paths
        assert "README.md" in file_paths
        
        # Check that .git was excluded
        assert not any(".git" in str(f.relative_path) for f in repo._files)
    
    def test_include_patterns(self, sample_repo):
        """Test include pattern filtering."""
        repo = Repository(sample_repo).include("src/")
        repo._collect_files()
        
        file_paths = [str(f.relative_path) for f in repo._files]
        
        # Should only include files in src/
        assert "src/core.py" in file_paths
        assert "src/utils.py" in file_paths
        assert "main.py" not in file_paths
        assert "README.md" not in file_paths
    
    def test_exclude_patterns(self, sample_repo):
        """Test exclude pattern filtering."""
        repo = Repository(sample_repo).exclude("tests/", "*.md")
        repo._collect_files()
        
        file_paths = [str(f.relative_path) for f in repo._files]
        
        # Should exclude tests/ and .md files
        assert "main.py" in file_paths
        assert "src/core.py" in file_paths
        assert "tests/test_core.py" not in file_paths
        assert "README.md" not in file_paths
    
    def test_language_detection(self, sample_repo):
        """Test programming language detection."""
        repo = Repository(sample_repo)
        repo._collect_files()
        
        # Find Python files
        py_files = [f for f in repo._files if f.language == "python"]
        assert len(py_files) > 0
        
        # Find Markdown files
        md_files = [f for f in repo._files if f.language == "markdown"]
        assert len(md_files) > 0
    
    def test_analyze(self, sample_repo):
        """Test repository analysis."""
        repo = Repository(sample_repo)
        result = repo.analyze()
        
        assert result is repo
        assert repo._analyzed is True
        assert len(repo._files) > 0
    
    def test_analyze_with_importance_scoring(self, sample_repo):
        """Test analysis with importance scoring."""
        repo = Repository(sample_repo).with_importance_scoring()
        repo.analyze()
        
        # Check that files have importance scores
        scored_files = [f for f in repo._files if f.importance is not None]
        assert len(scored_files) > 0
        
        # main.py should have high importance
        main_file = next((f for f in repo._files 
                          if f.relative_path.name == "main.py"), None)
        if main_file and main_file.importance:
            assert main_file.importance.total_score > 0.5
    
    def test_to_dict(self, sample_repo):
        """Test conversion to dictionary."""
        repo = Repository(sample_repo).name("TestProject").analyze()
        data = repo.to_dict()
        
        assert isinstance(data, dict)
        assert 'metadata' in data
        assert 'files' in data
        
        assert data['metadata']['name'] == "TestProject"
        assert data['metadata']['path'] == str(sample_repo)
        assert data['metadata']['file_count'] == len(repo._files)
        
        assert len(data['files']) == len(repo._files)
        
        # Check file structure
        for file_dict in data['files']:
            assert 'path' in file_dict
            assert 'language' in file_dict
            assert 'size' in file_dict
    
    def test_to_dict_with_statistics(self, sample_repo):
        """Test dictionary with statistics."""
        repo = Repository(sample_repo).with_stats(True).analyze()
        data = repo.to_dict()
        
        assert 'statistics' in data
        stats = data['statistics']
        
        assert 'total_files' in stats
        assert 'total_size' in stats
        assert 'languages' in stats
        
        # Check language statistics
        if 'python' in stats['languages']:
            assert 'count' in stats['languages']['python']
            assert 'size' in stats['languages']['python']
    
    def test_to_dict_without_content(self, sample_repo):
        """Test dictionary without file content."""
        repo = Repository(sample_repo).with_content(False).analyze()
        data = repo.to_dict()
        
        # Files should not have content
        for file_dict in data['files']:
            assert 'content' not in file_dict or file_dict['content'] is None
    
    def test_calculate_statistics(self, sample_repo):
        """Test statistics calculation."""
        repo = Repository(sample_repo).analyze()
        stats = repo._calculate_statistics()
        
        assert stats['total_files'] == len(repo._files)
        assert stats['total_size'] > 0
        assert len(stats['languages']) > 0
    
    def test_summarize_file_placeholder(self, sample_repo):
        """Test file summarization (placeholder for now)."""
        repo = Repository(sample_repo)
        
        entry = FileEntry(
            path=Path("test.py"),
            relative_path=Path("test.py"),
            content="test content"
        )
        
        summary = repo._summarize_file(entry)
        assert summary == "[Summarized: test.py]"