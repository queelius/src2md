"""
Unit tests for file importance scoring.
"""
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import tempfile

from src2md.strategies.importance import (
    ImportanceScorer, ImportanceWeights, FileImportance
)


class TestImportanceWeights:
    """Test ImportanceWeights class."""
    
    def test_default_weights(self):
        """Test default weight values."""
        weights = ImportanceWeights()
        assert weights.entrypoint == 1.0
        assert weights.exports == 0.8
        assert weights.imports == 0.6
        assert weights.documentation == 0.7
        assert weights.complexity == 0.5
        assert weights.recency == 0.4
        assert weights.size_penalty == -0.3
        assert weights.test_file == 0.3
        assert weights.config_file == 0.5
        assert weights.generated_file == 0.1
    
    def test_normalize(self):
        """Test weight normalization."""
        weights = ImportanceWeights()
        weights.entrypoint = 2.0
        weights.exports = 1.0
        weights.normalize()
        
        # Check that positive weights sum to approximately 1.0
        positive_weights = [
            weights.entrypoint, weights.exports, weights.imports,
            weights.documentation, weights.complexity, weights.recency,
            weights.test_file, weights.config_file, weights.generated_file
        ]
        assert abs(sum(positive_weights) - 1.0) < 0.01


class TestImportanceScorer:
    """Test ImportanceScorer class."""
    
    def test_initialization(self):
        """Test scorer initialization."""
        scorer = ImportanceScorer()
        assert scorer.weights is not None
        
        # With custom weights
        custom_weights = ImportanceWeights(entrypoint=2.0)
        scorer = ImportanceScorer(weights=custom_weights)
        assert scorer.weights.entrypoint == 2.0
    
    def test_check_entrypoint(self):
        """Test entrypoint detection."""
        scorer = ImportanceScorer()
        
        # Exact matches
        assert scorer._check_entrypoint(Path("main.py")) == 1.0
        assert scorer._check_entrypoint(Path("app.py")) == 1.0
        assert scorer._check_entrypoint(Path("index.js")) == 1.0
        assert scorer._check_entrypoint(Path("server.py")) == 1.0
        
        # Partial matches
        assert scorer._check_entrypoint(Path("main_module.py")) == 0.5
        assert scorer._check_entrypoint(Path("index_handler.js")) == 0.5
        
        # No match
        assert scorer._check_entrypoint(Path("utils.py")) == 0.0
        assert scorer._check_entrypoint(Path("test.py")) == 0.0
    
    def test_is_test(self):
        """Test test file detection."""
        scorer = ImportanceScorer()
        
        assert scorer._is_test(Path("test_module.py")) is True
        assert scorer._is_test(Path("module_test.py")) is True
        assert scorer._is_test(Path("file.test.js")) is True
        assert scorer._is_test(Path("file.spec.js")) is True
        assert scorer._is_test(Path("TestClass.java")) is True
        
        assert scorer._is_test(Path("module.py")) is False
        assert scorer._is_test(Path("main.js")) is False
    
    def test_is_config(self):
        """Test config file detection."""
        scorer = ImportanceScorer()
        
        assert scorer._is_config(Path("app.config.js")) is True
        assert scorer._is_config(Path("settings.ini")) is True
        assert scorer._is_config(Path("config.yaml")) is True
        assert scorer._is_config(Path(".eslintrc")) is True
        assert scorer._is_config(Path(".env")) is True
        
        assert scorer._is_config(Path("main.py")) is False
        assert scorer._is_config(Path("utils.js")) is False
    
    def test_is_generated(self):
        """Test generated file detection."""
        scorer = ImportanceScorer()
        
        assert scorer._is_generated(Path("proto.pb.go")) is True
        assert scorer._is_generated(Path("schema_pb2.py")) is True
        assert scorer._is_generated(Path("types.generated.ts")) is True
        assert scorer._is_generated(Path("bundle.min.js")) is True
        
        assert scorer._is_generated(Path("main.py")) is False
        assert scorer._is_generated(Path("utils.go")) is False
    
    def test_count_python_exports(self, sample_python_content):
        """Test Python export counting."""
        scorer = ImportanceScorer()
        
        score = scorer._count_python_exports(sample_python_content)
        # Should find SampleClass and exported_function (not _internal_function)
        assert score > 0
        assert score <= 1.0
    
    def test_count_python_imports(self, sample_python_content):
        """Test Python import counting."""
        scorer = ImportanceScorer()
        
        score = scorer._count_python_imports(sample_python_content)
        # Should find 'import os', 'import sys', 'from typing import ...'
        assert score > 0
        assert score <= 1.0
    
    def test_calculate_python_complexity(self, sample_python_content):
        """Test Python complexity calculation."""
        scorer = ImportanceScorer()
        
        score = scorer._calculate_python_complexity(sample_python_content)
        # Should find if statement in exported_function
        assert score > 0
        assert score <= 1.0
    
    def test_count_generic_exports(self, sample_javascript_content):
        """Test generic export counting."""
        scorer = ImportanceScorer()
        
        score = scorer._count_generic_exports(sample_javascript_content)
        # Should find 'export class', 'export function', 'export const'
        assert score > 0
        assert score <= 1.0
    
    def test_score_documentation(self):
        """Test documentation scoring."""
        scorer = ImportanceScorer()
        
        # Well-documented code (good ratio)
        well_documented = '''"""Module docstring."""
# This function does something
def function():
    """Function docstring."""
    # Implementation comment
    return 42
'''
        score1 = scorer._score_documentation(well_documented)
        assert score1 > 0.5
        
        # No documentation
        no_docs = '''def function():
    return 42
'''
        score2 = scorer._score_documentation(no_docs)
        assert score2 < 0.5
        
        # Over-documented (too many comments)
        over_documented = '\n'.join(['# Comment'] * 50 + ['x = 1'])
        score3 = scorer._score_documentation(over_documented)
        assert score3 < 1.0  # Should be penalized
    
    def test_check_recency(self):
        """Test file recency checking."""
        scorer = ImportanceScorer()
        
        # Create a temporary file with known modification time
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        # Test with current file (just created)
        score = scorer._check_recency(tmp_path)
        assert score == 1.0  # Modified within last day
        
        # Clean up
        tmp_path.unlink()
    
    def test_calculate_size_penalty(self):
        """Test size penalty calculation."""
        scorer = ImportanceScorer()
        
        # Small file - no penalty
        assert scorer._calculate_size_penalty(5_000) == 0.0
        
        # Medium file - small penalty
        assert scorer._calculate_size_penalty(25_000) == -0.3
        
        # Large file - bigger penalty
        assert scorer._calculate_size_penalty(75_000) == -0.6
        
        # Huge file - maximum penalty
        assert scorer._calculate_size_penalty(200_000) == -1.0
    
    def test_score_file(self, sample_python_content):
        """Test complete file scoring."""
        scorer = ImportanceScorer()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp_path.write_text(sample_python_content)
        
        # Score the file
        importance = scorer.score(tmp_path, sample_python_content)
        
        assert isinstance(importance, FileImportance)
        assert importance.path == tmp_path
        assert 0.0 <= importance.total_score <= 1.0
        assert len(importance.factors) > 0
        
        # Check that factors are calculated
        assert 'is_entrypoint' in importance.factors
        assert 'has_exports' in importance.factors
        assert 'import_count' in importance.factors
        assert 'documentation' in importance.factors
        assert 'complexity' in importance.factors
        
        # Clean up
        tmp_path.unlink()
    
    def test_rank_files(self):
        """Test file ranking."""
        scorer = ImportanceScorer()
        
        # Create mock FileImportance objects
        file1 = FileImportance(Path("main.py"), 0.9, {})
        file2 = FileImportance(Path("utils.py"), 0.5, {})
        file3 = FileImportance(Path("test.py"), 0.3, {})
        file4 = FileImportance(Path("config.py"), 0.7, {})
        
        files = [file2, file4, file1, file3]
        ranked = scorer.rank_files(files)
        
        # Should be sorted by score descending
        assert ranked[0] == file1  # 0.9
        assert ranked[1] == file4  # 0.7
        assert ranked[2] == file2  # 0.5
        assert ranked[3] == file3  # 0.3
    
    def test_weighted_sum(self):
        """Test weighted sum calculation."""
        scorer = ImportanceScorer()
        
        factors = {
            'is_entrypoint': 1.0,
            'has_exports': 0.5,
            'import_count': 0.3,
            'test_file': 0.0,
            'size_penalty': -0.5,
        }
        
        score = scorer._weighted_sum(factors)
        
        # Score should be between 0 and 1
        assert 0.0 <= score <= 1.0