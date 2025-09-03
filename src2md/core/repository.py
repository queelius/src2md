"""
Repository abstraction with fluent API for elegant code analysis.
"""
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Callable, Any
from dataclasses import dataclass, field
import fnmatch
import os

from .context import ContextWindow, ContextOptimizer, TokenCounter
from ..strategies.importance import ImportanceScorer, FileImportance
from ..formatters.base import Formatter


@dataclass
class FileEntry:
    """Represents a file in the repository."""
    path: Path
    relative_path: Path
    content: Optional[str] = None
    size: int = 0
    language: Optional[str] = None
    importance: Optional[FileImportance] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Repository:
    """
    Repository analysis with fluent API.
    
    Example:
        repo = Repository("/path/to/project")
        result = (repo
            .name("MyProject")
            .include("src/", "lib/")
            .exclude("tests/")
            .with_importance_scoring()
            .optimize_for(ContextWindow.GPT_4)
            .to_markdown())
    """
    
    def __init__(self, path: Union[str, Path]):
        """Initialize repository from path."""
        self.path = Path(path).resolve()
        if not self.path.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not self.path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        self._name = self.path.name
        self._branch = None
        self._include_patterns = []
        self._exclude_patterns = ['.git', '__pycache__', '*.pyc', '.env']
        self._files: List[FileEntry] = []
        self._analyzed = False
        self._importance_scorer = None
        self._context_optimizer = None
        self._summarization_enabled = False
        self._metadata = {}
        
        # Configuration
        self._config = {
            'include_content': True,
            'include_stats': True,
            'include_dependencies': False,
            'preserve_ratio': 0.85,
        }
    
    def name(self, name: str) -> 'Repository':
        """Set repository name."""
        self._name = name
        return self
    
    def branch(self, branch: str) -> 'Repository':
        """Set branch name (for documentation)."""
        self._branch = branch
        return self
    
    def include(self, *patterns: str) -> 'Repository':
        """
        Add include patterns.
        
        Args:
            patterns: Glob patterns or directory names to include
        """
        self._include_patterns.extend(patterns)
        return self
    
    def exclude(self, *patterns: str) -> 'Repository':
        """
        Add exclude patterns.
        
        Args:
            patterns: Glob patterns or directory names to exclude
        """
        self._exclude_patterns.extend(patterns)
        return self
    
    def with_importance_scoring(self, scorer: Optional[ImportanceScorer] = None) -> 'Repository':
        """Enable importance scoring with optional custom scorer."""
        self._importance_scorer = scorer or ImportanceScorer()
        return self
    
    def with_dependency_graph(self) -> 'Repository':
        """Include dependency graph analysis."""
        self._config['include_dependencies'] = True
        return self
    
    def with_content(self, include: bool = True) -> 'Repository':
        """Include or exclude file contents."""
        self._config['include_content'] = include
        return self
    
    def with_stats(self, include: bool = True) -> 'Repository':
        """Include or exclude statistics."""
        self._config['include_stats'] = include
        return self
    
    def optimize_for(self, window: ContextWindow, 
                    preserve_ratio: float = 0.85) -> 'Repository':
        """
        Optimize for a specific context window.
        
        Args:
            window: Target context window
            preserve_ratio: Ratio of important content to preserve (0.0-1.0)
        """
        self._context_optimizer = ContextOptimizer(window)
        self._config['preserve_ratio'] = preserve_ratio
        return self
    
    def optimize_for_tokens(self, max_tokens: int, 
                           preserve_ratio: float = 0.85) -> 'Repository':
        """
        Optimize for a specific token limit.
        
        Args:
            max_tokens: Maximum number of tokens
            preserve_ratio: Ratio of important content to preserve
        """
        self._context_optimizer = ContextOptimizer.with_limit(max_tokens)
        self._config['preserve_ratio'] = preserve_ratio
        return self
    
    def prioritize(self, paths: List[str]) -> 'Repository':
        """
        Prioritize specific paths/files.
        
        Args:
            paths: List of paths to prioritize
        """
        self._metadata['priority_paths'] = paths
        return self
    
    def summarize_tests(self, enable: bool = True) -> 'Repository':
        """Enable test file summarization."""
        self._metadata['summarize_tests'] = enable
        return self
    
    def summarize_docs(self, enable: bool = True) -> 'Repository':
        """Enable documentation summarization."""
        self._metadata['summarize_docs'] = enable
        return self
    
    def analyze(self) -> 'Repository':
        """
        Analyze the repository.
        
        This method must be called before formatting output.
        """
        if self._analyzed:
            return self
        
        # Collect files
        self._collect_files()
        
        # Score importance if enabled
        if self._importance_scorer:
            self._score_importance()
        
        # Optimize for context window if enabled
        if self._context_optimizer:
            self._optimize_context()
        
        self._analyzed = True
        return self
    
    def _collect_files(self):
        """Collect all files matching patterns."""
        for root, dirs, files in os.walk(self.path):
            root_path = Path(root)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            for file in files:
                file_path = root_path / file
                relative_path = file_path.relative_to(self.path)
                
                # Check exclusion
                if self._should_exclude(str(relative_path)):
                    continue
                
                # Check inclusion
                if self._include_patterns and not self._should_include(str(relative_path)):
                    continue
                
                # Read content if needed
                content = None
                if self._config['include_content']:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                    except (UnicodeDecodeError, IOError):
                        continue
                
                # Detect language
                language = self._detect_language(file_path)
                
                entry = FileEntry(
                    path=file_path,
                    relative_path=relative_path,
                    content=content,
                    size=file_path.stat().st_size,
                    language=language
                )
                
                self._files.append(entry)
    
    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded."""
        for pattern in self._exclude_patterns:
            if fnmatch.fnmatch(path, pattern) or pattern in path:
                return True
        return False
    
    def _should_include(self, path: str) -> bool:
        """Check if path should be included."""
        if not self._include_patterns:
            return True
        
        for pattern in self._include_patterns:
            if fnmatch.fnmatch(path, pattern) or pattern in path:
                return True
        return False
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'objc',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
        }
        
        suffix = file_path.suffix.lower()
        return extension_map.get(suffix)
    
    def _score_importance(self):
        """Score file importance."""
        if not self._importance_scorer:
            return
        
        for entry in self._files:
            if entry.content:
                entry.importance = self._importance_scorer.score(
                    entry.path,
                    entry.content,
                    self.path
                )
    
    def _optimize_context(self):
        """Optimize files for context window."""
        if not self._context_optimizer:
            return
        
        # Sort files by importance
        if self._importance_scorer:
            self._files.sort(key=lambda f: f.importance.total_score if f.importance else 0, 
                           reverse=True)
        
        # Check priority paths
        priority_paths = self._metadata.get('priority_paths', [])
        if priority_paths:
            priority_files = []
            other_files = []
            
            for entry in self._files:
                is_priority = any(
                    pattern in str(entry.relative_path) 
                    for pattern in priority_paths
                )
                if is_priority:
                    priority_files.append(entry)
                else:
                    other_files.append(entry)
            
            self._files = priority_files + other_files
        
        # Apply summarization based on token budget
        total_tokens = 0
        preserve_ratio = self._config['preserve_ratio']
        
        for i, entry in enumerate(self._files):
            if not entry.content:
                continue
            
            tokens = TokenCounter.count(entry.content)
            
            # Check if we can fit full content
            if self._context_optimizer.can_fit(entry.content):
                total_tokens += tokens
            else:
                # Summarize if needed
                if i / len(self._files) > preserve_ratio:
                    # Summarize less important files
                    entry.summary = self._summarize_file(entry)
                    entry.content = None  # Clear original content
    
    def _summarize_file(self, entry: FileEntry) -> str:
        """Summarize a file based on its type."""
        # TODO: Implement actual summarization strategies
        # For now, return a placeholder
        return f"[Summarized: {entry.relative_path}]"
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with repository analysis
        """
        if not self._analyzed:
            self.analyze()
        
        result = {
            'metadata': {
                'name': self._name,
                'path': str(self.path),
                'branch': self._branch,
                'file_count': len(self._files),
            },
            'files': []
        }
        
        # Add statistics if enabled
        if self._config['include_stats']:
            result['statistics'] = self._calculate_statistics()
        
        # Add files
        for entry in self._files:
            file_dict = {
                'path': str(entry.relative_path),
                'language': entry.language,
                'size': entry.size,
            }
            
            if entry.content:
                file_dict['content'] = entry.content
            elif entry.summary:
                file_dict['summary'] = entry.summary
            
            if entry.importance:
                file_dict['importance'] = entry.importance.total_score
            
            result['files'].append(file_dict)
        
        return result
    
    def _calculate_statistics(self) -> Dict:
        """Calculate repository statistics."""
        stats = {
            'total_files': len(self._files),
            'total_size': sum(f.size for f in self._files),
            'languages': {},
        }
        
        # Count by language
        for entry in self._files:
            if entry.language:
                if entry.language not in stats['languages']:
                    stats['languages'][entry.language] = {
                        'count': 0,
                        'size': 0
                    }
                stats['languages'][entry.language]['count'] += 1
                stats['languages'][entry.language]['size'] += entry.size
        
        # Add token usage if optimizer is present
        if self._context_optimizer:
            stats['context'] = self._context_optimizer.get_summary()
        
        return stats
    
    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        from ..formatters.markdown import MarkdownFormatter
        formatter = MarkdownFormatter()
        return formatter.format(self.to_dict())
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert to JSON format."""
        from ..formatters.json import JSONFormatter
        formatter = JSONFormatter(pretty=pretty)
        return formatter.format(self.to_dict())
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        from ..formatters.html import HTMLFormatter
        formatter = HTMLFormatter()
        return formatter.format(self.to_dict())