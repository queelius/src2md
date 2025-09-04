"""
Intelligent code summarization strategies for context optimization.
"""
import ast
import re
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class SummarizationLevel(Enum):
    """Level of detail for summarization."""
    FULL = "full"  # No summarization
    SIGNATURES = "signatures"  # Function/class signatures only
    DOCSTRINGS = "docstrings"  # Signatures + docstrings
    OUTLINE = "outline"  # High-level structure only
    MINIMAL = "minimal"  # Bare minimum information


@dataclass
class SummarizationConfig:
    """Configuration for summarization."""
    level: SummarizationLevel = SummarizationLevel.DOCSTRINGS
    preserve_imports: bool = True
    preserve_exports: bool = True
    preserve_docstrings: bool = True
    preserve_comments: bool = False
    max_line_length: int = 120
    target_compression_ratio: float = 0.3  # Target 30% of original size


class CodeSummarizer(ABC):
    """Abstract base class for code summarizers."""
    
    def __init__(self, config: Optional[SummarizationConfig] = None):
        self.config = config or SummarizationConfig()
    
    @abstractmethod
    def summarize(self, content: str, **kwargs) -> str:
        """Summarize the code content."""
        pass
    
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Check if this summarizer can handle the file type."""
        pass
    
    def estimate_compression(self, content: str) -> float:
        """Estimate the compression ratio achievable."""
        summary = self.summarize(content)
        return len(summary) / len(content) if content else 0.0


class PythonSummarizer(CodeSummarizer):
    """Summarizer for Python code using AST analysis."""
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix in {'.py', '.pyw'}
    
    def summarize(self, content: str, **kwargs) -> str:
        """Summarize Python code preserving structure and key information."""
        try:
            tree = ast.parse(content)
            return self._summarize_ast(tree, content)
        except SyntaxError:
            # Fall back to regex-based summarization
            return self._regex_summarize(content)
    
    def _summarize_ast(self, tree: ast.AST, source: str) -> str:
        """Summarize using AST analysis."""
        lines = []
        source_lines = source.splitlines()
        
        # Preserve module docstring
        if ast.get_docstring(tree):
            lines.append('"""')
            lines.append(ast.get_docstring(tree))
            lines.append('"""')
            lines.append('')
        
        # Preserve imports if configured
        if self.config.preserve_imports:
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if hasattr(node, 'lineno'):
                        import_line = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else ""
                        if import_line and import_line not in lines:
                            lines.append(import_line)
            if lines and lines[-1]:  # Add blank line after imports
                lines.append('')
        
        # Process based on summarization level
        if self.config.level == SummarizationLevel.FULL:
            return source
        elif self.config.level == SummarizationLevel.MINIMAL:
            return self._minimal_summary(tree)
        elif self.config.level == SummarizationLevel.OUTLINE:
            return self._outline_summary(tree)
        else:
            return self._detailed_summary(tree, source_lines)
    
    def _minimal_summary(self, tree: ast.AST) -> str:
        """Create minimal summary with just names."""
        items = []
        
        # Add imports if configured
        if self.config.preserve_imports:
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            items.append(f"import {alias.name}")
                    else:
                        module = node.module or ''
                        names = ', '.join(alias.name for alias in node.names)
                        items.append(f"from {module} import {names}")
        
        # Add classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                items.append(f"class {node.name}")
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_') or node.name.startswith('__'):
                    items.append(f"def {node.name}()")
        return '\n'.join(items)
    
    def _outline_summary(self, tree: ast.AST) -> str:
        """Create outline with class and function names."""
        lines = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                lines.append(f"class {node.name}:")
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        params = ', '.join(arg.arg for arg in item.args.args)
                        lines.append(f"    def {item.name}({params}): ...")
                lines.append('')
            elif isinstance(node, ast.FunctionDef):
                params = ', '.join(arg.arg for arg in node.args.args)
                lines.append(f"def {node.name}({params}): ...")
                lines.append('')
        
        return '\n'.join(lines)
    
    def _detailed_summary(self, tree: ast.AST, source_lines: List[str]) -> str:
        """Create detailed summary with signatures and docstrings."""
        lines = []
        
        # Add imports first if configured
        if self.config.preserve_imports:
            import_lines = []
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if hasattr(node, 'lineno') and node.lineno <= len(source_lines):
                        import_lines.append(source_lines[node.lineno - 1])
            if import_lines:
                lines.extend(import_lines)
                lines.append('')  # Blank line after imports
        
        # Add classes and functions
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                lines.extend(self._summarize_class(node, source_lines))
            elif isinstance(node, ast.FunctionDef):
                lines.extend(self._summarize_function(node, source_lines))
            elif isinstance(node, ast.AsyncFunctionDef):
                lines.extend(self._summarize_function(node, source_lines, async_def=True))
        
        return '\n'.join(lines)
    
    def _summarize_class(self, node: ast.ClassDef, source_lines: List[str]) -> List[str]:
        """Summarize a class definition."""
        lines = []
        
        # Class signature with decorators
        for decorator in node.decorator_list:
            if hasattr(decorator, 'id'):
                lines.append(f"@{decorator.id}")
        
        # Class definition with base classes
        bases = []
        for base in node.bases:
            if hasattr(base, 'id'):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id if hasattr(base.value, 'id') else '...'}.{base.attr}")
        
        base_str = f"({', '.join(bases)})" if bases else ""
        lines.append(f"class {node.name}{base_str}:")
        
        # Class docstring
        docstring = ast.get_docstring(node)
        if docstring and self.config.preserve_docstrings:
            lines.append(f'    """{docstring[:200]}..."""' if len(docstring) > 200 else f'    """{docstring}"""')
        
        # Class methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_lines = self._summarize_function(item, source_lines, indent="    ", async_def=isinstance(item, ast.AsyncFunctionDef))
                lines.extend(method_lines)
        
        lines.append('')
        return lines
    
    def _summarize_function(self, node: ast.FunctionDef, source_lines: List[str], 
                           indent: str = "", async_def: bool = False) -> List[str]:
        """Summarize a function definition."""
        lines = []
        
        # Skip private methods unless they're special methods
        if node.name.startswith('_') and not node.name.startswith('__'):
            if self.config.level != SummarizationLevel.DOCSTRINGS:
                return []
        
        # Function decorators
        for decorator in node.decorator_list:
            if hasattr(decorator, 'id'):
                lines.append(f"{indent}@{decorator.id}")
        
        # Function signature
        params = []
        for arg in node.args.args:
            param = arg.arg
            if arg.annotation:
                if hasattr(arg.annotation, 'id'):
                    param += f": {arg.annotation.id}"
            params.append(param)
        
        # Add defaults indication
        if node.args.defaults:
            num_defaults = len(node.args.defaults)
            for i in range(num_defaults):
                params[-(i+1)] += "=..."
        
        returns = ""
        if node.returns:
            if hasattr(node.returns, 'id'):
                returns = f" -> {node.returns.id}"
        
        def_keyword = "async def" if async_def else "def"
        signature = f"{indent}{def_keyword} {node.name}({', '.join(params)}){returns}:"
        lines.append(signature)
        
        # Function docstring
        docstring = ast.get_docstring(node)
        if docstring and self.config.preserve_docstrings:
            # Truncate long docstrings
            if len(docstring) > 150:
                docstring = docstring[:150] + "..."
            lines.append(f'{indent}    """{docstring}"""')
            lines.append(f"{indent}    ...")
        else:
            lines.append(f"{indent}    ...")
        
        return lines
    
    def _regex_summarize(self, content: str) -> str:
        """Fallback regex-based summarization for invalid Python."""
        lines = []
        
        # Extract imports
        if self.config.preserve_imports:
            import_pattern = r'^(from .* import .*|import .*)$'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                lines.append(match.group(0))
            
            if lines:
                lines.append('')
        
        # Extract class definitions
        class_pattern = r'^class\s+(\w+).*?:'
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            lines.append(f"class {class_name}: ...")
        
        # Extract top-level functions (even incomplete ones)
        func_pattern = r'^def\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            lines.append(f"def {func_name}(...): ...")
        
        return '\n'.join(lines) if lines else "# Could not parse Python code"


class JavaScriptSummarizer(CodeSummarizer):
    """Summarizer for JavaScript/TypeScript code."""
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix in {'.js', '.jsx', '.ts', '.tsx', '.mjs'}
    
    def summarize(self, content: str, **kwargs) -> str:
        """Summarize JavaScript/TypeScript code."""
        lines = []
        file_path = kwargs.get('file_path')
        
        # Preserve imports/exports
        if self.config.preserve_imports:
            for line in content.splitlines():
                if re.match(r'^\s*(import|export|const\s+.*\s+=\s+require)', line):
                    lines.append(line)
        
        if lines:
            lines.append('')
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends = match.group(2)
            if extends:
                lines.append(f"class {class_name} extends {extends} {{ ... }}")
            else:
                lines.append(f"class {class_name} {{ ... }}")
        
        # Extract function declarations
        func_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)',  # function declarations
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',  # arrow functions
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function',  # function expressions
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                if not func_name.startswith('_'):
                    lines.append(f"function {func_name}(...) {{ ... }}")
        
        # Extract React components (for JSX/TSX)
        if file_path and file_path.suffix in {'.jsx', '.tsx'}:
            component_pattern = r'(?:function|const)\s+([A-Z]\w+)\s*[=\(]'
            for match in re.finditer(component_pattern, content):
                comp_name = match.group(1)
                # Don't add if already listed as a function
                if f"function {comp_name}" not in '\n'.join(lines):
                    lines.append(f"Component: {comp_name}")
        
        return '\n'.join(lines) if lines else "// Summarized JavaScript/TypeScript file"


class ConfigSummarizer(CodeSummarizer):
    """Summarizer for configuration files."""
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix in {'.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg'}
    
    def summarize(self, content: str, **kwargs) -> str:
        """Summarize configuration files by extracting key structure."""
        file_path = kwargs.get('file_path', Path('config'))
        
        if file_path.suffix == '.json':
            return self._summarize_json(content)
        elif file_path.suffix in {'.yaml', '.yml'}:
            return self._summarize_yaml(content)
        elif file_path.suffix == '.toml':
            return self._summarize_toml(content)
        else:
            return self._summarize_generic(content)
    
    def _summarize_json(self, content: str) -> str:
        """Summarize JSON configuration."""
        try:
            data = json.loads(content)
            return self._summarize_dict(data, max_depth=2)
        except json.JSONDecodeError:
            return "// Invalid JSON configuration"
    
    def _summarize_dict(self, data: Dict, indent: int = 0, max_depth: int = 2) -> str:
        """Recursively summarize dictionary structure."""
        if indent >= max_depth:
            return "  " * indent + "..."
        
        lines = []
        for key, value in data.items():
            prefix = "  " * indent
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                if indent < max_depth - 1:
                    lines.append(self._summarize_dict(value, indent + 1, max_depth))
                else:
                    lines.append(f"{prefix}  ...")
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    lines.append(f"{prefix}{key}: [{len(value)} items]")
                else:
                    lines.append(f"{prefix}{key}: [{len(value)} values]")
            else:
                # Show actual values for important keys
                important_keys = {'version', 'name', 'type', 'engine', 'main', 'entry'}
                if key.lower() in important_keys:
                    lines.append(f"{prefix}{key}: {value}")
                else:
                    lines.append(f"{prefix}{key}: ...")
        
        return '\n'.join(lines)
    
    def _summarize_yaml(self, content: str) -> str:
        """Summarize YAML configuration."""
        lines = []
        current_indent = 0
        
        for line in content.splitlines()[:50]:  # First 50 lines
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            
            indent = len(line) - len(stripped)
            if ':' in stripped and not stripped.startswith('-'):
                key = stripped.split(':')[0].strip()
                if indent <= 4:  # Top-level and second-level keys
                    lines.append(line.split(':')[0] + ': ...')
        
        return '\n'.join(lines) if lines else "# YAML configuration summary"
    
    def _summarize_toml(self, content: str) -> str:
        """Summarize TOML configuration."""
        lines = []
        for line in content.splitlines()[:30]:
            if line.startswith('['):  # Section headers
                lines.append(line)
            elif '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                lines.append(f"{key} = ...")
        
        return '\n'.join(lines) if lines else "# TOML configuration summary"
    
    def _summarize_generic(self, content: str) -> str:
        """Generic configuration file summarization."""
        lines = []
        for line in content.splitlines()[:30]:
            if line and not line.strip().startswith('#'):
                if '=' in line or ':' in line:
                    lines.append(line.split('=')[0].split(':')[0].strip() + " = ...")
        
        return '\n'.join(lines) if lines else "# Configuration file summary"


class TestSummarizer(CodeSummarizer):
    """Summarizer specifically for test files."""
    
    def can_handle(self, file_path: Path) -> bool:
        name = file_path.stem.lower()
        return 'test' in name or 'spec' in name
    
    def summarize(self, content: str, **kwargs) -> str:
        """Summarize test files by extracting test names and structure."""
        lines = ["# Test Summary"]
        
        # Extract test class names
        test_class_pattern = r'class\s+(Test\w+|.*Test\w*|.*Spec\w*)'
        for match in re.finditer(test_class_pattern, content, re.MULTILINE):
            lines.append(f"TestClass: {match.group(1)}")
        
        # Extract test function names (Python)
        test_func_pattern = r'def\s+(test_\w+|.*_test|.*_spec)\s*\('
        for match in re.finditer(test_func_pattern, content, re.MULTILINE):
            lines.append(f"  - {match.group(1)}")
        
        # Extract test descriptions (JavaScript/TypeScript)
        js_test_patterns = [
            r'(?:it|test|describe)\s*\([\'"`]([^\'"`]+)[\'"`]',
            r'(?:it|test|describe)\s*\([\'"`]([^\'"`]+)[\'"`]',
        ]
        
        for pattern in js_test_patterns:
            for match in re.finditer(pattern, content):
                lines.append(f"  - {match.group(1)}")
        
        return '\n'.join(lines) if len(lines) > 1 else "# Test file"


class DocumentationSummarizer(CodeSummarizer):
    """Summarizer for documentation files."""
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix in {'.md', '.rst', '.txt', '.adoc'}
    
    def summarize(self, content: str, **kwargs) -> str:
        """Summarize documentation by extracting headers and key sections."""
        lines = []
        
        # Extract headers (Markdown style)
        header_pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            header = match.group(2)
            indent = "  " * (level - 1)
            lines.append(f"{indent}- {header}")
        
        if not lines:
            # Try extracting first paragraph
            paragraphs = content.split('\n\n')
            if paragraphs:
                first_para = paragraphs[0][:200]
                lines.append(first_para + "..." if len(paragraphs[0]) > 200 else first_para)
        
        return '\n'.join(lines) if lines else "# Documentation file"


class SummarizationStrategy:
    """Orchestrates different summarizers based on file type."""
    
    def __init__(self, config: Optional[SummarizationConfig] = None):
        self.config = config or SummarizationConfig()
        self.summarizers = [
            PythonSummarizer(self.config),
            JavaScriptSummarizer(self.config),
            ConfigSummarizer(self.config),
            TestSummarizer(self.config),
            DocumentationSummarizer(self.config),
        ]
    
    def summarize(self, file_path: Path, content: str, 
                  target_ratio: Optional[float] = None) -> str:
        """Select appropriate summarizer and summarize content."""
        # Override target ratio if specified
        if target_ratio is not None:
            self.config.target_compression_ratio = target_ratio
        
        # Find appropriate summarizer
        for summarizer in self.summarizers:
            if summarizer.can_handle(file_path):
                return summarizer.summarize(content, file_path=file_path)
        
        # Default: return first N lines
        lines = content.splitlines()
        max_lines = int(len(lines) * self.config.target_compression_ratio)
        if max_lines > 0:
            result = '\n'.join(lines[:max_lines])
            return result + "\n# ... (truncated)"
        
        return "# File contents summarized"
    
    def can_summarize(self, file_path: Path) -> bool:
        """Check if file can be summarized."""
        return any(s.can_handle(file_path) for s in self.summarizers)