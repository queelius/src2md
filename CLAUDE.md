# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**src2md** is a tool that converts source code repositories into structured, context-window-optimized representations for LLMs. It addresses the fundamental challenge of fitting meaningful codebases into limited context windows while preserving the most important information.

### Core Value Proposition

While agentic LLMs can navigate codebases with tools, there's immense value in creating intelligently compressed, self-contained snapshots that classical LLMs can reason about in a single context. This enables:

1. **Single-shot understanding** without hundreds of tool calls
2. **Cross-repository analysis** by combining multiple codebases
3. **Cost-effective analysis** (one API call vs. many)
4. **Reproducible snapshots** for consistent analysis
5. **Context-aware summarization** to fit within token limits

## Architecture Vision

### Core Abstractions (Pythonic & Elegant)

```python
# src2md/core/
├── analyzer.py       # Repository analysis with AST parsing
├── context.py        # Context window management
├── pipeline.py       # Processing pipeline with transforms
├── summarizer.py     # LLM-powered and rule-based summarization
└── repository.py     # Repository abstraction

# src2md/formatters/
├── base.py          # Abstract formatter interface
├── markdown.py      # Markdown output
├── json.py          # JSON/JSONL output
├── html.py          # HTML output
└── llm.py           # LLM-optimized formats

# src2md/strategies/
├── importance.py    # File importance scoring
├── chunking.py      # Semantic chunking strategies
└── compression.py   # Compression strategies
```

### Context Window Management

The key innovation is intelligent context window management with multiple strategies:

```python
from src2md import Repository, ContextWindow

# Basic usage with automatic optimization
repo = Repository("/path/to/project")
result = repo.optimize_for(ContextWindow.GPT4)  # 128K tokens

# Advanced with custom strategies
result = (repo
    .with_context_limit(100_000)  # tokens
    .prioritize(["core/", "api/"])  # Important paths
    .summarize_tests()  # Compress test files
    .summarize_docs()   # Compress documentation
    .include_dependencies()  # Add dependency context
    .analyze())

# Multi-tier compression
result = (repo
    .with_context_limit(50_000)
    .use_strategy("progressive")  # Progressive summarization
    .tier(1).include(["*.py", "*.js"])  # Full content
    .tier(2).summarize(["tests/", "docs/"])  # Summarized
    .tier(3).metadata_only(["node_modules/", ".git/"])  # Just structure
    .analyze())
```

### Importance Scoring System

Files are scored based on multiple factors:

```python
class ImportanceScorer:
    """Score files by importance for context window optimization."""
    
    def score(self, file_path: Path, content: str) -> float:
        factors = {
            'is_entrypoint': self._check_entrypoint(file_path),  # main.py, index.js
            'has_exports': self._count_exports(content),  # Public API
            'import_count': self._count_imports(content),  # Dependencies
            'documentation': self._score_documentation(content),  # Comments/docs
            'complexity': self._calculate_complexity(content),  # Cyclomatic
            'recency': self._check_recency(file_path),  # Recent changes
            'size_penalty': self._size_penalty(len(content)),  # Penalize huge files
            'test_file': self._is_test(file_path),  # Lower priority
            'config_file': self._is_config(file_path),  # Medium priority
        }
        return self._weighted_sum(factors)
```

### Summarization Strategies

Multiple summarization approaches for different file types:

```python
class SummarizationPipeline:
    """Intelligent summarization based on file type and importance."""
    
    strategies = {
        'tests': TestSummarizer(),      # Extract test names and assertions
        'docs': DocSummarizer(),         # Extract headings and key points
        'config': ConfigSummarizer(),    # Extract key settings
        'data': DataSummarizer(),        # Schema and sample records
        'generated': GeneratedSummarizer(),  # Just signatures
        'vendor': VendorSummarizer(),    # Package names and versions
    }
    
    def summarize(self, file: File, target_ratio: float = 0.2):
        """Compress file to target ratio of original size."""
        if file.importance > 0.8:
            return file.content  # Don't summarize critical files
        
        strategy = self._select_strategy(file)
        return strategy.summarize(file, target_ratio)
```

### LLM-Powered Summarization

Optional integration with LLMs for intelligent summarization:

```python
class LLMSummarizer:
    """Use LLM to summarize code intelligently."""
    
    def __init__(self, model="gpt-3.5-turbo", max_tokens=500):
        self.model = model
        self.max_tokens = max_tokens
    
    def summarize_chunk(self, code: str, context: str) -> str:
        prompt = f"""
        Summarize this code, preserving:
        - Public API signatures
        - Core business logic
        - Important comments
        - Key algorithms
        
        Context: {context}
        Code: {code}
        
        Output a concise summary in {self.max_tokens} tokens.
        """
        return self.llm.complete(prompt)
```

### Fluent API Design

The API supports elegant method chaining:

```python
from src2md import Repository, MultiRepo, ContextWindow

# Single repository with fluent API
analysis = (Repository("/path/to/project")
    .name("MyProject")
    .branch("feature/new-api")
    .include("src/", "lib/")
    .exclude("tests/", "docs/")
    .with_importance_scoring()
    .with_dependency_graph()
    .optimize_for(ContextWindow.CLAUDE_3, preserve_ratio=0.8)
    .to_markdown())

# Multi-repository analysis
analysis = (MultiRepo()
    .add("frontend", "/path/to/frontend")
    .add("backend", "/path/to/backend")
    .add("shared", "/path/to/shared")
    .with_cross_references()
    .with_api_boundaries()
    .with_shared_types()
    .optimize_for_tokens(150_000)
    .to_json())

# Progressive loading for huge codebases
analysis = (Repository("/massive/codebase")
    .stream()  # Enable streaming mode
    .chunk_size(10_000)  # Tokens per chunk
    .on_chunk(lambda chunk: process(chunk))
    .analyze())
```

### Multi-Repository Support

Sophisticated multi-repo analysis:

```python
class MultiRepoAnalyzer:
    """Analyze relationships across multiple repositories."""
    
    def analyze_relationships(self) -> Dict:
        return {
            'dependency_graph': self._build_dependency_graph(),
            'api_contracts': self._extract_api_contracts(),
            'shared_types': self._find_shared_types(),
            'integration_points': self._find_integration_points(),
            'deployment_topology': self._analyze_deployment(),
        }
    
    def optimize_context(self, token_limit: int) -> Dict:
        """Intelligently distribute token budget across repos."""
        importance_scores = self._score_repo_importance()
        token_allocation = self._allocate_tokens(importance_scores, token_limit)
        
        return {
            repo.name: repo.optimize_for_tokens(allocation)
            for repo, allocation in token_allocation.items()
        }
```

## Development Commands

```bash
# Setup development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run with context optimization
src2md /path/to/project --max-tokens 100000 --strategy progressive
src2md /path/to/project --optimize-for gpt-4 --preserve-ratio 0.9
src2md /path/to/project --summarize-tests --summarize-docs

# Multi-repo analysis
src2md multi --add frontend:/path/to/fe --add backend:/path/to/be --max-tokens 150000

# Testing
pytest                          # Run all tests
pytest -xvs                     # Verbose with stop on first failure
pytest --cov=src2md            # With coverage
pytest tests/test_context.py   # Test context management

# Code quality
black src2md/                   # Format code
ruff check src2md/             # Lint code  
mypy src2md/                   # Type checking
```

## Configuration

### .src2mdrc.yaml
```yaml
# Context optimization settings
context:
  default_window: gpt-4  # or claude-3, gpt-3.5, custom
  max_tokens: 100000
  preserve_ratio: 0.85  # Keep 85% of important content

# Importance scoring weights
importance:
  entrypoint: 1.0
  exports: 0.8
  imports: 0.6
  documentation: 0.7
  complexity: 0.5
  recency: 0.4
  tests: 0.3

# Summarization settings
summarization:
  enable_llm: false  # Use LLM for summarization
  llm_model: gpt-3.5-turbo
  compression_ratio: 0.2  # Target 20% of original size
  
# File patterns
patterns:
  always_include:
    - "README.md"
    - "package.json"
    - "requirements.txt"
  always_summarize:
    - "*.test.js"
    - "*_test.py"
    - "*.spec.ts"
  always_exclude:
    - "*.pyc"
    - "node_modules/"
    - ".git/"
```

## Use Cases

### 1. Code Review with Context Limits
```python
# Fit a large PR into GPT-4's context
review = (Repository(".")
    .diff("main", "feature/branch")
    .optimize_for(ContextWindow.GPT4)
    .include_related_files()  # Add context files
    .to_markdown())
```

### 2. Cross-Repository Refactoring
```python
# Understand API boundaries before refactoring
analysis = (MultiRepo()
    .add_all("/workspace/services/*")
    .analyze_api_contracts()
    .find_breaking_changes("v2.0")
    .to_json())
```

### 3. Documentation Generation
```python
# Generate comprehensive docs within token limit
docs = (Repository(".")
    .with_docstrings()
    .with_type_hints()
    .with_examples()
    .optimize_for_tokens(50_000)
    .to_html())
```

### 4. Architecture Analysis
```python
# Analyze system architecture across repos
architecture = (MultiRepo()
    .add_github("org/frontend")
    .add_github("org/backend")
    .add_github("org/infrastructure")
    .with_dependency_graph()
    .with_deployment_topology()
    .visualize())
```

## Implementation Priorities

1. **Phase 1**: Core context window management
   - Token counting and limits
   - Basic importance scoring
   - Simple summarization strategies

2. **Phase 2**: Intelligent summarization
   - AST-based analysis
   - File-type-specific strategies
   - Preservation of critical information

3. **Phase 3**: LLM integration
   - Optional LLM-powered summarization
   - Context-aware compression
   - Semantic chunking

4. **Phase 4**: Multi-repository support
   - Cross-repo analysis
   - Dependency graphs
   - API boundary detection

5. **Phase 5**: Advanced features
   - Streaming for huge codebases
   - Incremental updates
   - Custom plugins/strategies

## Design Principles

1. **Progressive Enhancement**: Works without LLM, better with it
2. **Graceful Degradation**: Intelligently degrades when hitting limits
3. **Pythonic**: Clean, idiomatic Python with type hints
4. **Composable**: Small, focused classes that compose well
5. **Extensible**: Plugin architecture for custom strategies
6. **Testable**: High test coverage with property-based tests

## Dependencies

- **Core**: pathspec, rich, pyyaml
- **AST Analysis**: ast, astroid (for Python), tree-sitter (multi-language)
- **LLM Integration**: openai, anthropic (optional)
- **Utilities**: tiktoken (token counting), pygments (syntax highlighting)