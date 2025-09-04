# src2md Documentation

Welcome to the comprehensive documentation for **src2md** - a powerful tool for converting source code repositories into LLM-optimized formats with intelligent context management and summarization.

## Documentation Index

### 📚 User Documentation

- **[Usage Guide](./USAGE_GUIDE.md)** - Comprehensive guide with examples and best practices
- **[Getting Started](#getting-started)** - Quick start guide for new users
- **[Configuration Guide](#configuration)** - Configuration files and environment variables
- **[CLI Reference](#cli-reference)** - Command-line interface documentation

### 🔧 API Documentation

- **[API Reference](./api/README.md)** - Complete API documentation index
- **[Context Window Management](./api/context.md)** - Token management and optimization
- **[Summarization Strategies](./api/summarization.md)** - AST-based and language-specific summarization
- **[LLM Integration](./api/llm_summarizer.md)** - OpenAI and Anthropic integration

### 🚀 Features

- **[v2.0 Release Notes](#v20-features)** - New features and improvements
- **[Examples](../examples/)** - Code examples and recipes
- **[Best Practices](#best-practices)** - Recommended patterns and tips

## Getting Started

### Installation

```bash
# Basic installation
pip install src2md

# With LLM support
pip install src2md[llm]

# With all optional dependencies
pip install src2md[all]
```

### Quick Start

```python
from src2md import Repository, ContextWindow

# Basic usage - convert repository to markdown
output = Repository("./my-project").analyze().to_markdown()

# Optimize for GPT-4's context window
output = (Repository("./my-project")
    .optimize_for(ContextWindow.GPT_4)
    .analyze()
    .to_markdown())

# Enable intelligent summarization
output = (Repository("./my-project")
    .with_summarization(compression_ratio=0.3)
    .optimize_for_tokens(100_000)
    .analyze()
    .to_markdown())
```

## v2.0 Features

### 🎯 Context Window Optimization
- Smart truncation that preserves code structure
- Predefined windows for GPT-4, Claude 3, and other LLMs
- Token-accurate counting with tiktoken
- Progressive compression strategies

### 📝 Intelligent Summarization
- **AST-based analysis** for Python with multiple compression levels
- **Multi-language support**: JavaScript, TypeScript, JSON, YAML
- **Specialized summarizers** for test files and documentation
- **LLM-powered compression** with OpenAI and Anthropic

### ⚡ Enhanced Fluent API
```python
repo = (Repository("./project")
    .with_importance_scoring()
    .with_summarization(
        compression_ratio=0.3,
        preserve_important=True,
        use_llm=True
    )
    .prioritize(["src/core/", "api/"])
    .optimize_for(ContextWindow.GPT_4)
    .analyze())
```

### 🔧 New CLI Flags
```bash
# Summarization options
src2md . --summarize --compression-ratio 0.3
src2md . --summarize-tests --summarize-docs
src2md . --use-llm --llm-model gpt-3.5-turbo

# Context optimization
src2md . --gpt4 --importance
src2md . --tokens 50000 --preserve-important
```

## Configuration

### Environment Variables

```bash
# LLM API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Default Settings
export SRC2MD_DEFAULT_CONTEXT="gpt-4"
export SRC2MD_COMPRESSION_RATIO="0.3"
export SRC2MD_USE_LLM="false"
```

### Configuration File (.src2mdrc)

```yaml
# Context optimization
context:
  default_window: gpt-4
  max_tokens: 100000
  preserve_ratio: 0.85

# Summarization
summarization:
  enabled: true
  compression_ratio: 0.3
  use_llm: false
  llm_model: gpt-3.5-turbo

# File importance weights
importance:
  entrypoint: 1.0
  exports: 0.8
  imports: 0.6
  documentation: 0.7
```

## CLI Reference

### Basic Commands

```bash
# Convert to markdown (default)
src2md /path/to/project

# Save to file
src2md /path/to/project -o output.md

# Different output formats
src2md /path/to/project --format json --pretty
src2md /path/to/project --format html
```

### Context Optimization

```bash
# Optimize for specific LLMs
src2md . --gpt4        # GPT-4 (128K tokens)
src2md . --gpt35       # GPT-3.5 (16K tokens)
src2md . --claude3     # Claude 3 (200K tokens)

# Custom token limit
src2md . --tokens 50000

# Enable importance scoring
src2md . --importance --prioritize "src/core/*"
```

### Summarization

```bash
# Enable summarization
src2md . --summarize --compression-ratio 0.3

# Selective summarization
src2md . --summarize-tests --summarize-docs

# LLM-powered summarization
src2md . --use-llm --llm-model gpt-3.5-turbo
```

## Best Practices

### 1. Progressive Optimization

Start simple and add features as needed:

```python
# Step 1: Basic analysis
repo = Repository("./project").analyze()

# Step 2: Add importance scoring
repo = repo.with_importance_scoring()

# Step 3: Add context optimization
repo = repo.optimize_for(ContextWindow.GPT_4)

# Step 4: Add summarization if needed
repo = repo.with_summarization(compression_ratio=0.3)
```

### 2. Cost-Effective LLM Usage

Use LLM summarization selectively:

```python
# Use LLM only for important files
repo = (Repository("./project")
    .with_importance_scoring()
    .with_summarization(
        use_llm=True,
        preserve_important=True  # Only use LLM for less important files
    ))
```

### 3. Validation

Always validate output quality:

```python
data = repo.to_dict()

# Check compression metrics
print(f"Files processed: {data['metadata']['file_count']}")
print(f"Compression ratio: {data['metadata'].get('compression_ratio', 1.0):.1%}")
print(f"Token usage: {data['metadata'].get('total_tokens', 0):,}")

# Verify important files are preserved
for file in data['source_files']:
    if file.get('importance_score', 0) > 0.8:
        assert not file.get('was_summarized'), f"Important file was summarized: {file['path']}"
```

## Architecture Overview

```
src2md/
├── core/
│   ├── repository.py      # Main Repository class with fluent API
│   ├── context.py         # Context window management
│   ├── analyzer.py        # Code analysis engine
│   └── pipeline.py        # Processing pipeline
├── strategies/
│   ├── summarization.py   # AST-based summarization
│   ├── llm_summarizer.py  # LLM-powered summarization
│   └── importance.py      # File importance scoring
├── formatters/
│   ├── markdown.py        # Markdown output
│   ├── json.py            # JSON/JSONL output
│   └── html.py            # HTML output
└── cli.py                 # Command-line interface
```

## Performance Tips

1. **Use token estimation** for faster processing with `estimate_tokens=True`
2. **Cache LLM responses** to avoid redundant API calls
3. **Process in batches** for better performance with large repositories
4. **Enable streaming** for huge codebases (coming soon)
5. **Use appropriate compression** - don't over-compress critical files

## Troubleshooting

### Common Issues

**Token Limit Exceeded**
- Use more aggressive summarization
- Exclude less important files
- Increase compression ratio

**LLM API Errors**
- Check API key configuration
- Implement fallback to AST-based summarization
- Monitor rate limits

**Memory Issues**
- Process large repositories in chunks
- Use streaming mode (when available)
- Reduce batch sizes

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/src2md/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/src2md/discussions)
- **Documentation**: [This documentation](./README.md)

## License

MIT License - see [LICENSE](../LICENSE) file for details.