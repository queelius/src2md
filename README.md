# src2md

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![PyPI](https://img.shields.io/pypi/v/src2md)
![Python Versions](https://img.shields.io/pypi/pyversions/src2md)
![Version](https://img.shields.io/badge/version-2.1.0-green.svg)

**src2md** is a powerful tool that converts source code repositories into structured, context-window-optimized representations for Large Language Models (LLMs). It addresses the fundamental challenge of fitting meaningful codebases into limited context windows while preserving the most important information through intelligent summarization, AST-based analysis, and optional LLM-powered compression.

## 🚀 **Features**

### New in v2.1
- **🎯 Context Window Optimization**: Intelligently fit codebases into LLM context windows with smart truncation
- **📝 Intelligent Summarization**: AST-based code analysis with multiple compression levels
- **🤖 LLM-Powered Compression**: Optional OpenAI/Anthropic integration for semantic summarization
- **⚡ Fluent API**: Elegant method chaining with new summarization methods
- **📊 File Importance Scoring**: Multi-factor analysis to prioritize critical files
- **🪟 Predefined LLM Windows**: Built-in support for GPT-4, Claude, and more
- **🔄 Progressive Summarization**: Multi-tier compression strategies for different file types

### Core Features
- **Multiple Output Formats**: JSON, JSONL, Markdown, HTML, and plain text
- **Smart Token Management**: Accurate token counting with tiktoken and structure-aware truncation
- **Multi-Language Support**: Specialized summarizers for Python, JavaScript, TypeScript, JSON, YAML
- **Code Statistics**: Automatic generation of project metrics and complexity analysis
- **Flexible Filtering**: Customizable include/exclude patterns
- **Rich CLI Interface**: Beautiful progress indicators and colored output

## 📦 **Installation**

Install via [PyPI](https://pypi.org/) using `pip`:

```bash
pip install src2md
```

## 🛠️ **Usage**

### Quick Start - Fluent API

```python
from src2md import Repository, ContextWindow

# Basic usage
output = Repository("/path/to/project").analyze().to_markdown()

# Optimize for GPT-4 context window
output = (Repository("/path/to/project")
    .optimize_for(ContextWindow.GPT_4)
    .analyze()
    .to_markdown())

# Full fluent API with all features
result = (Repository("/path/to/project")
    .name("MyProject")
    .branch("main")
    .include("src/", "lib/")
    .exclude("tests/", "*.log")
    .with_importance_scoring()
    .with_summarization(
        compression_ratio=0.3,  # Target 30% of original size
        preserve_important=True,  # Keep critical files intact
        use_llm=True  # Use LLM if available
    )
    .prioritize(["main.py", "core/"])
    .optimize_for_tokens(100_000)  # 100K token limit
    .analyze()
    .to_json(pretty=True))
```

### Command Line Interface

```bash
# Basic markdown generation
src2md /path/to/project -o documentation.md

# With context optimization
src2md /path/to/project --gpt4 -o optimized.md
src2md /path/to/project --claude3 --importance

# With intelligent summarization
src2md /path/to/project --summarize --compression-ratio 0.3
src2md /path/to/project --summarize-tests --summarize-docs

# With LLM-powered summarization (requires API key)
src2md /path/to/project --use-llm --llm-model gpt-3.5-turbo

# Multiple output formats
src2md /path/to/project --format json --pretty
src2md /path/to/project --format html -o docs.html
```

### Python API Examples

#### Basic Context Optimization

```python
from src2md import Repository, ContextWindow

# Optimize for different LLM context windows
repo = Repository("./my-project")
output = repo.optimize_for(ContextWindow.CLAUDE_3).analyze().to_markdown()

# Custom token limit with importance scoring
repo = (Repository("./my-project")
    .with_importance_scoring()
    .optimize_for_tokens(50_000)
    .analyze())
```

#### Intelligent Summarization

```python
# Enable smart summarization with compression
repo = (Repository("./my-project")
    .with_summarization(
        compression_ratio=0.3,  # Compress to 30% of original
        preserve_important=True,  # Keep critical files intact
        use_llm=False  # Use AST-based summarization
    )
    .optimize_for(ContextWindow.GPT_4)
    .analyze())

# Use LLM-powered summarization (requires API key)
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'

repo = (Repository("./my-project")
    .with_summarization(
        compression_ratio=0.2,  # More aggressive compression
        use_llm=True,
        llm_model="gpt-3.5-turbo"
    )
    .analyze())
```

#### Multi-Tier Compression Strategy

```python
# Configure different summarization levels for different file types
repo = (Repository("./my-project")
    .with_importance_scoring()
    .prioritize(["src/core/", "api/"])  # Critical paths
    .summarize_tests()  # Compress test files
    .summarize_docs()   # Compress documentation
    .with_summarization(
        compression_ratio=0.25,
        preserve_important=True
    )
    .optimize_for_tokens(100_000)
    .analyze())

# Access summarization metadata
data = repo.to_dict()
for file in data['source_files']:
    if file.get('was_summarized'):
        print(f"Summarized {file['path']}: {file['original_size']} -> {file['size']} bytes")
```

#### Generate Multiple Formats

```python
repo = Repository("./my-project").analyze()
markdown = repo.to_markdown()
json_data = repo.to_json()
html_doc = repo.to_html()

# Access raw data
data = repo.to_dict()
print(f"Files: {data['metadata']['file_count']}")
print(f"Token usage: {data['metadata'].get('total_tokens', 0)}")
print(f"Compression achieved: {data['metadata'].get('compression_ratio', 1.0):.1%}")
```

## 🎯 **Summarization Features**

### AST-Based Python Summarization

src2md uses Abstract Syntax Tree (AST) analysis to intelligently summarize Python code while preserving structure:

- **MINIMAL**: Only class/function signatures
- **OUTLINE**: Signatures with structural hierarchy  
- **DOCSTRINGS**: Signatures plus documentation
- **SIGNATURES**: Full signatures with type hints
- **FULL**: No summarization

### Multi-Language Support

Specialized summarizers for different file types:

- **Python**: AST-based analysis with import/export preservation
- **JavaScript/TypeScript**: Function and class extraction
- **JSON/YAML**: Schema extraction with sample data
- **Test Files**: Test name and assertion extraction
- **Documentation**: Heading and key point extraction

### Smart Truncation

When files must be truncated to fit token limits:

1. Preserves code structure (complete functions/classes)
2. Maintains syntax validity
3. Prioritizes public APIs over private methods
4. Keeps imports and exports intact

### LLM-Powered Summarization

Optional integration with OpenAI and Anthropic for semantic compression:

```bash
# Set API keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Use LLM summarization
src2md /path/to/project --use-llm --llm-model gpt-3.5-turbo
src2md /path/to/project --use-llm --llm-model claude-3-haiku-20240307
```

## 📊 **Output Formats**

### JSON

Structured data perfect for programmatic processing:

```json
{
  "metadata": {
    "project_name": "my-project",
    "generated_at": "2025-01-01T12:00:00",
    "patterns": {...}
  },
  "statistics": {
    "total_files": 42,
    "languages": {"python": {"count": 15, "total_size": 50000}},
    "project_complexity": 3.2
  },
  "documentation": [...],
  "source_files": [...]
}
```

### JSONL

One JSON object per line - perfect for streaming and big data tools:

```jsonl
{"type": "metadata", "data": {...}}
{"type": "statistics", "data": {...}}
{"type": "source_file", "data": {...}}
```

### HTML

Beautiful, styled documentation ready for the web with syntax highlighting and responsive design.

### Markdown

Clean, readable documentation compatible with GitHub, GitLab, and other platforms.

## 🔧 **Advanced Options**

### File Patterns

```bash
# Custom documentation patterns
src2md project --doc-pat '*.md' '*.rst' '*.txt'

# Specific source file types
src2md project --src-pat '*.py' '*.js' '*.ts'

# Ignore patterns
src2md project --ignore-pat '*.pyc' 'node_modules/' '.git/'
```

### Ignore Files

Create a `.src2mdignore` file in your project root:

```gitignore
# Dependencies
node_modules/
__pycache__/
*.pyc

# Build outputs
dist/
build/
*.egg-info/

# IDE files
.vscode/
.idea/
```

### Configuration

```bash
# Use custom ignore file
src2md project --ignore-file .gitignore

# Disable statistics
src2md project --no-stats

# Metadata only (no file contents)
src2md project --no-content
```

## 🎯 **Use Cases**

- **LLM Context**: Generate structured context for AI/ML models
- **Documentation**: Create beautiful project documentation
- **Code Analysis**: Extract metrics and statistics from codebases
- **Data Export**: Convert code to structured formats for analysis
- **Archive**: Create comprehensive snapshots of projects
- **CI/CD**: Generate documentation automatically in build pipelines

## 📈 **Statistics & Metrics**

src2md automatically generates:

- **File Metrics**: Counts by type and language
- **Code Complexity**: Cyclomatic complexity scores
- **Token Usage**: Actual token counts for LLM context
- **Compression Stats**: Before/after summarization metrics
- **Importance Scores**: File prioritization rankings
- **Language Breakdown**: Distribution of code by language
- **Structure Analysis**: Dependency and module relationships

## 🤝 **Migration from v0.x**

The new version is backward compatible. Existing commands work unchanged:

```bash
# This still works exactly as before
src2md project -o docs.md --doc-pat '*.md' --src-pat '*.py'
```

New features are opt-in through additional flags and the Python API.

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.
