"""
File importance scoring for intelligent context optimization.
"""
import re
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import ast


@dataclass
class ImportanceWeights:
    """Configurable weights for importance scoring factors."""
    entrypoint: float = 1.0
    exports: float = 0.8
    imports: float = 0.6
    documentation: float = 0.7
    complexity: float = 0.5
    recency: float = 0.4
    size_penalty: float = -0.3
    test_file: float = 0.3
    config_file: float = 0.5
    generated_file: float = 0.1
    
    def normalize(self):
        """Normalize weights to sum to 1.0 for positive weights."""
        positive_sum = sum(w for w in self.__dict__.values() if w > 0)
        if positive_sum > 0:
            scale = 1.0 / positive_sum
            for key in self.__dict__:
                if self.__dict__[key] > 0:
                    self.__dict__[key] *= scale


@dataclass
class FileImportance:
    """Importance score and breakdown for a file."""
    path: Path
    total_score: float
    factors: Dict[str, float] = field(default_factory=dict)
    
    def __repr__(self):
        return f"FileImportance({self.path.name}, score={self.total_score:.2f})"


class ImportanceScorer:
    """Score files by importance for context window optimization."""
    
    # Common entrypoint patterns
    ENTRYPOINT_PATTERNS = [
        'main.py', '__main__.py', 'app.py', 'server.py', 'cli.py',
        'index.js', 'index.ts', 'main.js', 'main.ts', 'app.js',
        'main.go', 'main.rs', 'Main.java', 'Program.cs'
    ]
    
    # Common test file patterns
    TEST_PATTERNS = [
        r'test_.*\.py$', r'.*_test\.py$', r'.*\.test\.[jt]s$',
        r'.*\.spec\.[jt]s$', r'.*_spec\.rb$', r'Test.*\.java$', r'.*Test\.java$'
    ]
    
    # Common config file patterns
    CONFIG_PATTERNS = [
        r'.*\.config\.[jt]s$', r'.*\.conf$', r'.*\.ini$', r'.*\.toml$',
        r'.*\.yaml$', r'.*\.yml$', r'.*\.json$', r'.*rc$', r'.*\.env$'
    ]
    
    # Common generated file patterns
    GENERATED_PATTERNS = [
        r'.*\.pb\.go$', r'.*_pb2\.py$', r'.*\.generated\.*', 
        r'.*\.g\.[jt]s$', r'.*\.min\.[jt]s$', r'.*\.bundle\.[jt]s$'
    ]
    
    def __init__(self, weights: Optional[ImportanceWeights] = None):
        """Initialize with optional custom weights."""
        self.weights = weights or ImportanceWeights()
        # Only normalize if using default weights
        if weights is None:
            self.weights.normalize()
    
    def score(self, file_path: Path, content: str, 
              base_path: Optional[Path] = None) -> FileImportance:
        """
        Score a file's importance.
        
        Args:
            file_path: Path to the file
            content: File content
            base_path: Base path for relative calculations
            
        Returns:
            FileImportance with score and factor breakdown
        """
        factors = {}
        
        # Check if it's an entrypoint
        factors['is_entrypoint'] = self._check_entrypoint(file_path)
        
        # Analyze code structure (for Python files)
        if file_path.suffix == '.py':
            factors['has_exports'] = self._count_python_exports(content)
            factors['import_count'] = self._count_python_imports(content)
            factors['complexity'] = self._calculate_python_complexity(content)
        else:
            # Basic analysis for other languages
            factors['has_exports'] = self._count_generic_exports(content)
            factors['import_count'] = self._count_generic_imports(content)
            factors['complexity'] = self._calculate_generic_complexity(content)
        
        # Documentation score
        factors['documentation'] = self._score_documentation(content)
        
        # File metadata
        factors['recency'] = self._check_recency(file_path)
        factors['size_penalty'] = self._calculate_size_penalty(len(content))
        
        # File type classification
        factors['test_file'] = 1.0 if self._is_test(file_path) else 0.0
        factors['config_file'] = 1.0 if self._is_config(file_path) else 0.0
        factors['generated_file'] = 1.0 if self._is_generated(file_path) else 0.0
        
        # Calculate weighted sum
        total_score = self._weighted_sum(factors)
        
        return FileImportance(
            path=file_path,
            total_score=total_score,
            factors=factors
        )
    
    def _check_entrypoint(self, file_path: Path) -> float:
        """Check if file is likely an entrypoint (0.0-1.0)."""
        file_name = file_path.name
        
        # Exact match
        if file_name in self.ENTRYPOINT_PATTERNS:
            return 1.0
        
        # Partial match (e.g., contains 'main')
        if 'main' in file_name.lower() or 'index' in file_name.lower():
            return 0.5
        
        return 0.0
    
    def _count_python_exports(self, content: str) -> float:
        """Count Python exports (classes, functions) normalized to 0.0-1.0."""
        try:
            tree = ast.parse(content)
            exports = 0
            
            for node in ast.walk(tree):
                # Count top-level classes and functions
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith('_'):  # Public exports
                        exports += 1
            
            # Normalize (cap at 20 exports for max score)
            return min(exports / 20.0, 1.0)
        except:
            return 0.0
    
    def _count_generic_exports(self, content: str) -> float:
        """Count exports in non-Python files."""
        patterns = [
            r'\bexport\s+(class|function|const|let|var)\b',  # JS/TS
            r'\bpublic\s+(class|interface|enum)\b',  # Java/C#
            r'\bfunc\s+[A-Z]',  # Go (exported functions)
            r'\bpub\s+(fn|struct|enum)\b',  # Rust
        ]
        
        exports = 0
        for pattern in patterns:
            exports += len(re.findall(pattern, content))
        
        # Normalize
        return min(exports / 20.0, 1.0)
    
    def _count_python_imports(self, content: str) -> float:
        """Count Python imports normalized to 0.0-1.0."""
        try:
            tree = ast.parse(content)
            imports = sum(1 for node in ast.walk(tree) 
                         if isinstance(node, (ast.Import, ast.ImportFrom)))
            # Normalize (cap at 30 imports)
            return min(imports / 30.0, 1.0)
        except:
            return 0.0
    
    def _count_generic_imports(self, content: str) -> float:
        """Count imports in non-Python files."""
        patterns = [
            r'\bimport\s+',  # JS/TS/Java
            r'\brequire\s*\(',  # JS
            r'\buse\s+',  # Rust/PHP
            r'\binclude\s+',  # C/C++
            r'#include\s+',  # C/C++
        ]
        
        imports = 0
        for pattern in patterns:
            imports += len(re.findall(pattern, content))
        
        # Normalize
        return min(imports / 30.0, 1.0)
    
    def _calculate_python_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity for Python code."""
        try:
            tree = ast.parse(content)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                # Each decision point adds to complexity
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                   ast.ExceptHandler, ast.With, ast.AsyncWith)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    # Each and/or adds a branch
                    complexity += len(node.values) - 1
            
            # Normalize (cap at 50 for max complexity)
            return min(complexity / 50.0, 1.0)
        except:
            return 0.0
    
    def _calculate_generic_complexity(self, content: str) -> float:
        """Estimate complexity for non-Python code."""
        # Count control flow keywords
        keywords = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bswitch\b', r'\bcase\b',
            r'\bfor\b', r'\bwhile\b', r'\bdo\b', r'\btry\b', r'\bcatch\b',
            r'\bexcept\b', r'\bfinally\b'
        ]
        
        complexity = 1
        for keyword in keywords:
            complexity += len(re.findall(keyword, content, re.IGNORECASE))
        
        # Normalize
        return min(complexity / 50.0, 1.0)
    
    def _score_documentation(self, content: str) -> float:
        """Score documentation quality (comments, docstrings)."""
        lines = content.split('\n')
        total_lines = len(lines)
        
        if total_lines == 0:
            return 0.0
        
        doc_lines = 0
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check for docstring markers
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                doc_lines += 1
            elif in_docstring:
                doc_lines += 1
            # Check for comments
            elif stripped.startswith('#') or stripped.startswith('//'):
                doc_lines += 1
            elif '/*' in stripped or '*/' in stripped:
                doc_lines += 1
        
        # Calculate ratio
        doc_ratio = doc_lines / total_lines
        
        # Good documentation is 10-30% of code
        if doc_ratio < 0.1:
            return doc_ratio * 10  # Scale up
        elif doc_ratio > 0.3:
            return 1.0 - (doc_ratio - 0.3) * 2  # Penalize over-documentation
        else:
            return 1.0
    
    def _check_recency(self, file_path: Path) -> float:
        """Check file recency (recently modified files are more important)."""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - mtime
            
            # Files modified in last day: 1.0
            # Files modified in last week: 0.7
            # Files modified in last month: 0.4
            # Older files: 0.1
            
            if age < timedelta(days=1):
                return 1.0
            elif age < timedelta(days=7):
                return 0.7
            elif age < timedelta(days=30):
                return 0.4
            else:
                return 0.1
        except:
            return 0.1
    
    def _calculate_size_penalty(self, size: int) -> float:
        """Calculate size penalty (huge files are less important)."""
        # Files over 10KB start getting penalized
        if size < 10_000:
            return 0.0
        elif size < 50_000:
            return -0.3
        elif size < 100_000:
            return -0.6
        else:
            return -1.0
    
    def _is_test(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        name = file_path.name
        return any(re.match(pattern, name) for pattern in self.TEST_PATTERNS)
    
    def _is_config(self, file_path: Path) -> bool:
        """Check if file is a configuration file."""
        name = file_path.name
        return any(re.match(pattern, name) for pattern in self.CONFIG_PATTERNS)
    
    def _is_generated(self, file_path: Path) -> bool:
        """Check if file is generated code."""
        name = file_path.name
        return any(re.match(pattern, name) for pattern in self.GENERATED_PATTERNS)
    
    def _weighted_sum(self, factors: Dict[str, float]) -> float:
        """Calculate weighted sum of factors."""
        score = 0.0
        
        weight_map = {
            'is_entrypoint': self.weights.entrypoint,
            'has_exports': self.weights.exports,
            'import_count': self.weights.imports,
            'documentation': self.weights.documentation,
            'complexity': self.weights.complexity,
            'recency': self.weights.recency,
            'size_penalty': self.weights.size_penalty,
            'test_file': self.weights.test_file,
            'config_file': self.weights.config_file,
            'generated_file': self.weights.generated_file,
        }
        
        for factor, value in factors.items():
            if factor in weight_map:
                score += value * weight_map[factor]
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def rank_files(self, files: List[FileImportance]) -> List[FileImportance]:
        """Rank files by importance score."""
        return sorted(files, key=lambda f: f.total_score, reverse=True)