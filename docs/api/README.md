# src2md API Reference

## Overview

src2md provides a comprehensive API for converting source code repositories into LLM-optimized formats with intelligent context management and summarization capabilities.

## Core Modules

### [Context Window Management](./context.md)
- `ContextWindow` - Predefined LLM context window sizes
- `TokenBudget` - Token allocation and management
- `TokenCounter` - Accurate token counting with tiktoken
- `ContextOptimizer` - Smart truncation and optimization

### [Summarization Strategies](./summarization.md)
- `SummarizationLevel` - Compression levels (MINIMAL to FULL)
- `SummarizationConfig` - Summarization behavior configuration
- `PythonSummarizer` - AST-based Python analysis
- `JavaScriptSummarizer` - JavaScript/TypeScript summarization
- `TestSummarizer` - Test file compression
- `JSONSummarizer` - JSON schema extraction
- `YAMLSummarizer` - YAML configuration summarization

### [LLM-Powered Summarization](./llm_summarizer.md)
- `LLMProvider` - OpenAI and Anthropic integration
- `LLMConfig` - LLM configuration and model selection
- `LLMSummarizer` - Intelligent semantic compression
- Cost optimization and caching strategies

## Repository API

### Core Classes

```python
from src2md import Repository, ContextWindow

# Main repository class with fluent API
repo = Repository("./project")
```

### Fluent API Methods

#### Configuration Methods

- `.name(name: str)` - Set project name
- `.branch(branch: str)` - Set git branch
- `.include(*patterns)` - Include file patterns
- `.exclude(*patterns)` - Exclude file patterns
- `.ignore_file(path: str)` - Use custom ignore file

#### Analysis Methods

- `.with_importance_scoring()` - Enable file importance analysis
- `.prioritize(paths: List[str])` - Mark important paths
- `.deprioritize(paths: List[str])` - Mark less important paths
- `.with_statistics()` - Enable code statistics

#### Context Optimization

- `.optimize_for(window: ContextWindow)` - Optimize for predefined window
- `.optimize_for_tokens(limit: int)` - Custom token limit
- `.with_smart_truncation()` - Enable structure-aware truncation

#### Summarization

- `.with_summarization(**kwargs)` - Enable summarization
- `.summarize_tests()` - Compress test files
- `.summarize_docs()` - Compress documentation
- `.with_llm_config(config: LLMConfig)` - Configure LLM

#### Output Methods

- `.analyze()` - Process repository
- `.to_markdown(**kwargs)` - Generate Markdown output
- `.to_json(pretty: bool = False)` - Generate JSON output
- `.to_html(**kwargs)` - Generate HTML output
- `.to_dict()` - Get raw dictionary data

## Quick Start Examples

### Basic Usage

```python
from src2md import Repository

# Simple conversion
output = Repository("./project").analyze().to_markdown()
```

### With Context Optimization

```python
from src2md import Repository, ContextWindow

output = (Repository("./project")
    .optimize_for(ContextWindow.GPT_4)
    .with_importance_scoring()
    .analyze()
    .to_markdown())
```

### With Summarization

```python
output = (Repository("./project")
    .with_summarization(
        compression_ratio=0.3,
        preserve_important=True,
        use_llm=True
    )
    .optimize_for_tokens(100_000)
    .analyze()
    .to_json())
```

## Data Structures

### Repository Output Dictionary

```python
{
    "metadata": {
        "project_name": str,
        "generated_at": str,
        "file_count": int,
        "total_size": int,
        "total_tokens": int,  # If optimization enabled
        "token_limit": int,    # If optimization enabled
        "compression_ratio": float,  # If summarization enabled
        "patterns": {
            "include": List[str],
            "exclude": List[str]
        }
    },
    "statistics": {
        "languages": Dict[str, Dict],
        "complexity": float,
        "file_types": Dict[str, int]
    },
    "documentation": List[Dict],
    "source_files": [
        {
            "path": str,
            "size": int,
            "language": str,
            "content": str,
            "importance_score": float,  # If scoring enabled
            "was_summarized": bool,     # If summarization enabled
            "original_size": int,       # If summarized
            "summarization_level": str  # If summarized
        }
    ]
}
```

## Environment Variables

### LLM Configuration

- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `SRC2MD_LLM_PROVIDER` - Default LLM provider
- `SRC2MD_LLM_MODEL` - Default model
- `SRC2MD_LLM_MAX_TOKENS` - Max tokens for LLM

### Default Settings

- `SRC2MD_DEFAULT_CONTEXT` - Default context window
- `SRC2MD_COMPRESSION_RATIO` - Default compression ratio
- `SRC2MD_USE_LLM` - Enable LLM by default

## Error Handling

### Common Exceptions

```python
from src2md.exceptions import (
    TokenLimitExceeded,      # Content exceeds token limit
    InvalidConfiguration,    # Invalid settings
    SummarizationError,      # Summarization failed
    LLMNotAvailable,         # LLM API unavailable
    FileNotFound,            # Repository/file not found
)

try:
    repo = Repository("./project").optimize_for_tokens(1000).analyze()
except TokenLimitExceeded as e:
    print(f"Cannot fit in {e.limit} tokens")
except SummarizationError as e:
    print(f"Summarization failed: {e}")
```

## Performance Considerations

### Token Counting

- Use `estimate_tokens=True` for faster, approximate counting
- Token counting is cached per encoding/model
- Batch processing is more efficient than individual files

### Summarization

- AST parsing is cached for Python files
- LLM responses are cached (if caching enabled)
- Parallel processing available for large repositories

### Memory Usage

- Large repositories are processed in chunks
- Streaming mode available for huge codebases
- File content is loaded on-demand when possible

## Best Practices

1. **Start with importance scoring** to prioritize critical files
2. **Use progressive compression** - start light, increase as needed
3. **Cache LLM responses** to reduce API costs
4. **Profile first** - understand your codebase before optimizing
5. **Validate output** - ensure critical information is preserved

## Version Compatibility

- Python 3.8+ required
- LLM features require `openai` or `anthropic` packages
- Token counting requires `tiktoken` package

## See Also

- [Usage Guide](../USAGE_GUIDE.md) - Comprehensive usage examples
- [CLI Reference](../CLI.md) - Command-line interface documentation
- [Configuration](../CONFIG.md) - Configuration file options
- [Examples](../../examples/) - Code examples and recipes