# src2md Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Context Optimization](#context-optimization)
4. [Summarization Strategies](#summarization-strategies)
5. [LLM Integration](#llm-integration)
6. [Advanced Patterns](#advanced-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Basic installation
pip install src2md

# With LLM support
pip install src2md[llm]

# Development installation
git clone https://github.com/yourusername/src2md
cd src2md
pip install -e ".[dev]"
```

### Quick Start

```python
from src2md import Repository, ContextWindow

# Simple conversion
repo = Repository("./my-project")
output = repo.analyze().to_markdown()
print(output)

# Save to file
repo.analyze().to_markdown(output_file="documentation.md")
```

## Basic Usage

### Command Line Interface

```bash
# Basic usage
src2md /path/to/project

# Save to file
src2md /path/to/project -o output.md

# Different formats
src2md /path/to/project --format json --pretty
src2md /path/to/project --format html -o docs.html

# Filter files
src2md /path/to/project --include "src/*.py" --exclude "tests/*"
```

### Python API

```python
from src2md import Repository

# Create repository
repo = Repository("./project")

# Fluent API for configuration
repo = (Repository("./project")
    .name("MyProject")
    .branch("main")
    .include("src/", "lib/")
    .exclude("tests/", "docs/")
    .analyze())

# Generate outputs
markdown = repo.to_markdown()
json_data = repo.to_json()
html = repo.to_html()
```

## Context Optimization

### Predefined Context Windows

```python
from src2md import Repository, ContextWindow

# Optimize for specific LLMs
gpt4_output = (Repository("./project")
    .optimize_for(ContextWindow.GPT_4)  # 128K tokens
    .analyze()
    .to_markdown())

claude_output = (Repository("./project")
    .optimize_for(ContextWindow.CLAUDE_3)  # 200K tokens
    .analyze()
    .to_markdown())

# Custom token limit
custom_output = (Repository("./project")
    .optimize_for_tokens(50_000)  # Custom 50K limit
    .analyze()
    .to_markdown())
```

### Importance Scoring

```python
# Enable importance scoring for better prioritization
repo = (Repository("./project")
    .with_importance_scoring()
    .prioritize(["src/core/", "src/api/"])  # Mark critical paths
    .deprioritize(["tests/", "docs/"])  # Mark less important
    .optimize_for(ContextWindow.GPT_4)
    .analyze())

# Check importance scores
data = repo.to_dict()
for file in data['source_files']:
    print(f"{file['path']}: importance={file.get('importance_score', 0):.2f}")
```

### Progressive Optimization

```python
# Try different optimization levels
def progressive_fit(project_path: str, target_tokens: int):
    """Progressively compress until it fits."""
    repo = Repository(project_path).with_importance_scoring()
    
    # Try increasing compression
    for ratio in [1.0, 0.7, 0.5, 0.3, 0.1]:
        result = (repo
            .with_summarization(compression_ratio=ratio)
            .optimize_for_tokens(target_tokens)
            .analyze())
        
        if result.fits_in_context():
            print(f"Achieved fit with {ratio:.0%} compression")
            return result
    
    raise ValueError(f"Cannot fit in {target_tokens} tokens")
```

## Summarization Strategies

### Basic Summarization

```python
# Enable summarization with default settings
repo = (Repository("./project")
    .with_summarization()  # Default: 30% compression
    .analyze())

# Custom compression ratio
repo = (Repository("./project")
    .with_summarization(
        compression_ratio=0.2,  # Compress to 20% of original
        preserve_important=True  # Don't compress important files
    )
    .analyze())
```

### Selective Summarization

```python
# Summarize only specific file types
repo = (Repository("./project")
    .summarize_tests()  # Compress test files
    .summarize_docs()   # Compress documentation
    .analyze())

# Custom summarization rules
from src2md.strategies.summarization import SummarizationConfig, SummarizationLevel

config = SummarizationConfig(
    level=SummarizationLevel.DOCSTRINGS,  # Keep docstrings
    preserve_imports=True,
    preserve_exports=True,
    target_compression_ratio=0.25
)

repo = (Repository("./project")
    .with_summarization_config(config)
    .analyze())
```

### Language-Specific Strategies

```python
# The system automatically selects appropriate summarizers
# based on file extensions

# Python: AST-based analysis
# - Preserves class/function signatures
# - Keeps docstrings based on level
# - Maintains import structure

# JavaScript/TypeScript: Pattern matching
# - Preserves exports and imports
# - Keeps component structures
# - Maintains API definitions

# JSON/YAML: Schema extraction
# - Converts data to schemas
# - Preserves structure
# - Shows sample values

# Example: Mixed project
repo = (Repository("./fullstack-app")
    .with_summarization()
    .analyze())

# Check which files were summarized
data = repo.to_dict()
for file in data['source_files']:
    if file.get('was_summarized'):
        print(f"Summarized: {file['path']} ({file['language']})")
```

## LLM Integration

### Setup

```bash
# Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Basic LLM Summarization

```python
# Enable LLM summarization
repo = (Repository("./project")
    .with_summarization(
        use_llm=True,
        llm_model="gpt-3.5-turbo"  # or "claude-3-haiku-20240307"
    )
    .analyze())
```

### Advanced LLM Configuration

```python
from src2md.strategies.llm_summarizer import LLMConfig, LLMProvider

# Custom LLM configuration
llm_config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    max_tokens=500,
    temperature=0.2,
    system_prompt="""Focus on:
    1. Public APIs and their contracts
    2. Core business logic
    3. Error handling patterns
    4. Security considerations"""
)

repo = (Repository("./project")
    .with_llm_config(llm_config)
    .with_summarization(use_llm=True)
    .analyze())
```

### Cost-Optimized LLM Usage

```python
def cost_aware_summarization(project_path: str):
    """Use LLM only for important files."""
    repo = Repository(project_path).with_importance_scoring().analyze()
    data = repo.to_dict()
    
    # Separate files by importance
    important_files = []
    regular_files = []
    
    for file in data['source_files']:
        if file.get('importance_score', 0) > 0.7:
            important_files.append(file)
        else:
            regular_files.append(file)
    
    # Use LLM for important files
    important_repo = (Repository(project_path)
        .include_files(important_files)
        .with_summarization(use_llm=True, compression_ratio=0.3)
        .analyze())
    
    # Use AST for regular files
    regular_repo = (Repository(project_path)
        .include_files(regular_files)
        .with_summarization(use_llm=False, compression_ratio=0.2)
        .analyze())
    
    # Combine results
    return combine_repos(important_repo, regular_repo)
```

## Advanced Patterns

### Multi-Repository Analysis

```python
# Analyze multiple related projects
def analyze_microservices(service_paths: list):
    """Analyze multiple microservices together."""
    results = {}
    total_tokens = 100_000  # Total budget
    tokens_per_service = total_tokens // len(service_paths)
    
    for path in service_paths:
        service_name = Path(path).name
        results[service_name] = (Repository(path)
            .name(service_name)
            .with_importance_scoring()
            .optimize_for_tokens(tokens_per_service)
            .analyze())
    
    # Combine into single document
    combined = "# Microservices Architecture\n\n"
    for name, repo in results.items():
        combined += f"## {name}\n\n"
        combined += repo.to_markdown()
        combined += "\n\n---\n\n"
    
    return combined
```

### Incremental Analysis

```python
# Analyze only changed files
def analyze_changes(repo_path: str, since_commit: str):
    """Analyze only files changed since a commit."""
    import subprocess
    
    # Get changed files
    result = subprocess.run(
        ["git", "diff", "--name-only", since_commit],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    changed_files = result.stdout.strip().split('\n')
    
    # Analyze only changed files
    repo = (Repository(repo_path)
        .include_files(changed_files)
        .with_summarization()
        .analyze())
    
    return repo.to_markdown()
```

### Custom Output Formats

```python
# Create custom output format
def to_obsidian_vault(repo: Repository) -> None:
    """Convert repository to Obsidian vault structure."""
    import os
    from pathlib import Path
    
    vault_path = Path("obsidian_vault")
    vault_path.mkdir(exist_ok=True)
    
    data = repo.to_dict()
    
    # Create index
    index = "# Code Vault\n\n"
    
    # Create file notes
    for file in data['source_files']:
        # Create folder structure
        file_path = Path(file['path'])
        note_path = vault_path / f"{file_path.stem}.md"
        note_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create note content
        content = f"# {file_path.name}\n\n"
        content += f"**Path**: `{file['path']}`\n"
        content += f"**Language**: {file.get('language', 'unknown')}\n"
        content += f"**Size**: {file['size']} bytes\n"
        if file.get('importance_score'):
            content += f"**Importance**: {file['importance_score']:.2f}\n"
        content += f"\n## Code\n\n```{file.get('language', '')}\n"
        content += file['content']
        content += "\n```\n"
        
        # Write note
        note_path.write_text(content)
        
        # Add to index
        index += f"- [[{file_path.stem}]] - {file['path']}\n"
    
    # Write index
    (vault_path / "README.md").write_text(index)
```

### Pipeline Integration

```python
# GitHub Actions example
def github_action_handler():
    """Handler for GitHub Actions."""
    import os
    import json
    
    # Get inputs from environment
    project_path = os.environ.get('INPUT_PATH', '.')
    output_format = os.environ.get('INPUT_FORMAT', 'markdown')
    context_window = os.environ.get('INPUT_CONTEXT', 'gpt-4')
    use_llm = os.environ.get('INPUT_USE_LLM', 'false').lower() == 'true'
    
    # Map context window
    context_map = {
        'gpt-4': ContextWindow.GPT_4,
        'gpt-3.5': ContextWindow.GPT_35,
        'claude-3': ContextWindow.CLAUDE_3,
    }
    
    # Process repository
    repo = (Repository(project_path)
        .with_importance_scoring()
        .optimize_for(context_map.get(context_window, ContextWindow.GPT_4)))
    
    if use_llm:
        repo = repo.with_summarization(use_llm=True)
    
    result = repo.analyze()
    
    # Generate output
    if output_format == 'json':
        output = result.to_json()
    elif output_format == 'html':
        output = result.to_html()
    else:
        output = result.to_markdown()
    
    # Write to output
    with open('output.txt', 'w') as f:
        f.write(output)
    
    # Set GitHub Action output
    print(f"::set-output name=result::{len(output)} bytes generated")
```

## Best Practices

### 1. Start Simple, Add Complexity

```python
# Start with basic analysis
repo = Repository("./project").analyze()

# Add features as needed
repo = (Repository("./project")
    .with_importance_scoring()  # Add importance
    .optimize_for(ContextWindow.GPT_4)  # Add optimization
    .with_summarization()  # Add compression
    .analyze())
```

### 2. Profile Before Optimizing

```python
# Understand your codebase first
repo = Repository("./project").analyze()
data = repo.to_dict()

print(f"Total files: {data['metadata']['file_count']}")
print(f"Total size: {data['metadata']['total_size']} bytes")
print(f"Estimated tokens: {data['metadata'].get('total_tokens', 'unknown')}")

# Then optimize based on needs
if data['metadata'].get('total_tokens', 0) > 100_000:
    print("Large codebase - aggressive summarization needed")
    repo = repo.with_summarization(compression_ratio=0.2)
```

### 3. Use Appropriate Compression

```python
def select_compression_strategy(file_count: int, total_tokens: int, target_tokens: int):
    """Select appropriate compression strategy."""
    ratio = target_tokens / total_tokens if total_tokens > 0 else 1.0
    
    if ratio >= 0.8:
        # Minor compression needed
        return {"compression_ratio": 0.8, "use_llm": False}
    elif ratio >= 0.5:
        # Moderate compression
        return {"compression_ratio": 0.5, "use_llm": False}
    elif ratio >= 0.3:
        # Significant compression
        return {"compression_ratio": 0.3, "use_llm": True, "preserve_important": True}
    else:
        # Extreme compression
        return {"compression_ratio": 0.1, "use_llm": True, "aggressive": True}
```

### 4. Monitor Quality

```python
# Implement quality checks
def validate_output(original_repo: Repository, compressed_repo: Repository):
    """Validate compression quality."""
    original = original_repo.to_dict()
    compressed = compressed_repo.to_dict()
    
    # Check compression ratio
    original_size = sum(f['size'] for f in original['source_files'])
    compressed_size = sum(f['size'] for f in compressed['source_files'])
    ratio = compressed_size / original_size if original_size > 0 else 0
    
    # Check file coverage
    original_files = {f['path'] for f in original['source_files']}
    compressed_files = {f['path'] for f in compressed['source_files']}
    coverage = len(compressed_files) / len(original_files) if original_files else 0
    
    # Check syntax validity (for code files)
    syntax_valid = all(
        is_valid_syntax(f['content'], f.get('language'))
        for f in compressed['source_files']
    )
    
    return {
        "compression_ratio": ratio,
        "file_coverage": coverage,
        "syntax_valid": syntax_valid,
        "quality_score": (coverage * 0.5 + (1 - ratio) * 0.3 + syntax_valid * 0.2)
    }
```

### 5. Cache Aggressively

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_summarize(content_hash: str, compression_ratio: float):
    """Cache summarization results."""
    # This will be cached in memory
    return summarize_content(content_hash, compression_ratio)

def process_with_cache(repo_path: str):
    """Process repository with caching."""
    repo = Repository(repo_path)
    data = repo.to_dict()
    
    for file in data['source_files']:
        # Create content hash
        content_hash = hashlib.sha256(
            file['content'].encode()
        ).hexdigest()
        
        # Use cached result if available
        file['summarized'] = cached_summarize(
            content_hash,
            compression_ratio=0.3
        )
```

## Troubleshooting

### Common Issues

#### 1. Token Limit Exceeded

```python
# Problem: Repository too large for context window
# Solution: Use progressive compression

def fit_large_repo(repo_path: str, target_window: ContextWindow):
    """Fit large repository into context window."""
    # Start with importance scoring
    repo = Repository(repo_path).with_importance_scoring()
    
    # Try progressive strategies
    strategies = [
        {"summarize_tests": True},
        {"summarize_docs": True},
        {"compression_ratio": 0.5},
        {"compression_ratio": 0.3},
        {"compression_ratio": 0.1, "use_llm": True},
    ]
    
    for strategy in strategies:
        test_repo = repo.copy()
        for key, value in strategy.items():
            if hasattr(test_repo, key):
                getattr(test_repo, key)(value)
        
        test_repo = test_repo.optimize_for(target_window).analyze()
        
        if test_repo.fits_in_context():
            return test_repo
    
    raise ValueError("Cannot fit repository in context window")
```

#### 2. LLM API Errors

```python
# Problem: LLM API failures
# Solution: Implement fallback strategy

def safe_llm_summarize(content: str, **kwargs):
    """Summarize with fallback on LLM failure."""
    try:
        # Try LLM first
        from src2md.strategies.llm_summarizer import LLMSummarizer
        summarizer = LLMSummarizer()
        if summarizer.is_available():
            return summarizer.summarize_code(content, **kwargs)
    except Exception as e:
        print(f"LLM failed: {e}, using fallback")
    
    # Fallback to AST-based
    try:
        from src2md.strategies.summarization import SummarizationStrategy
        strategy = SummarizationStrategy()
        return strategy.summarize(Path("temp.py"), content)
    except Exception as e:
        print(f"AST failed: {e}, using simple truncation")
    
    # Final fallback
    return content[:1000] + "\n# ... truncated"
```

#### 3. Memory Issues

```python
# Problem: Large repositories cause memory issues
# Solution: Use streaming processing

def stream_large_repo(repo_path: str, chunk_size: int = 10):
    """Process large repository in chunks."""
    from pathlib import Path
    
    all_files = list(Path(repo_path).rglob("*"))
    
    # Process in chunks
    for i in range(0, len(all_files), chunk_size):
        chunk_files = all_files[i:i + chunk_size]
        
        # Process chunk
        chunk_repo = (Repository(repo_path)
            .include_files([str(f) for f in chunk_files])
            .with_summarization()
            .analyze())
        
        # Yield chunk result
        yield chunk_repo.to_markdown()
```

### Performance Tips

1. **Use Token Estimation**: For faster processing, use token estimation instead of exact counting
2. **Batch Operations**: Process multiple files together for better performance
3. **Parallel Processing**: Use multiprocessing for large repositories
4. **Cache Results**: Cache summarization results to avoid reprocessing
5. **Profile First**: Understand your codebase structure before applying optimization

### Debug Mode

```python
# Enable verbose logging for debugging
import logging

logging.basicConfig(level=logging.DEBUG)

# Use debug mode in repository
repo = (Repository("./project")
    .debug(True)  # Enable debug output
    .with_summarization()
    .analyze())

# Check internal state
print(repo._debug_info())
```

## See Also

- [API Reference](./api/) - Detailed API documentation
- [Examples](./examples/) - Code examples and recipes
- [Architecture](./ARCHITECTURE.md) - System architecture overview
- [Contributing](./CONTRIBUTING.md) - How to contribute