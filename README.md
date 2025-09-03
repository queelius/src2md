# src2md

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![PyPI](https://img.shields.io/pypi/v/src2md)
![Python Versions](https://img.shields.io/pypi/pyversions/src2md)
![Version](https://img.shields.io/badge/version-2.0.0-green.svg)

**src2md** is a powerful tool that converts source code repositories into structured formats optimized for Large Language Models (LLMs). With intelligent context window management, file importance scoring, and a fluent API, it's the perfect tool for feeding code context to AI models.

## 🚀 **Features**

### New in v2.0
- **🎯 Context Window Optimization**: Intelligently fit codebases into LLM context windows
- **⚡ Fluent API**: Elegant method chaining for intuitive usage
- **📊 File Importance Scoring**: Multi-factor analysis to prioritize critical files
- **🪟 Predefined LLM Windows**: Built-in support for GPT-4, Claude, and more
- **🔄 Progressive Summarization**: Compress less important files to fit token limits

### Core Features
- **Multiple Output Formats**: JSON, JSONL, Markdown, HTML, and plain text
- **Smart Token Management**: Accurate token counting with tiktoken
- **Code Statistics**: Automatic generation of project metrics and complexity analysis
- **Flexible Filtering**: Customizable include/exclude patterns
- **Rich CLI Interface**: Beautiful progress indicators and colored output

## 📦 **Installation**

Install via [PyPI](https://pypi.org/) using `pip`:

```bash
pip install src2md
```

## 🛠️ **Usage**

### Quick Start - Fluent API (New in v2.0!)

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
    .prioritize(["main.py", "core/"])
    .optimize_for_tokens(100_000)  # 100K token limit
    .analyze()
    .to_json(pretty=True))
```

### Command Line Interface

```bash
# Basic markdown generation
src2md /path/to/project -o documentation.md

# With context optimization (coming soon in CLI)
src2md /path/to/project --optimize-for gpt-4 -o optimized.md

# Multiple output formats
src2md /path/to/project --format json --pretty
src2md /path/to/project --format html -o docs.html
```

### Python API Examples

```python
from src2md import Repository, ContextWindow

# Example 1: Optimize for Claude 3
repo = Repository("./my-project")
output = repo.optimize_for(ContextWindow.CLAUDE_3).analyze().to_markdown()

# Example 2: Custom token limit with importance scoring
repo = (Repository("./my-project")
    .with_importance_scoring()
    .optimize_for_tokens(50_000)
    .analyze())

# Example 3: Generate multiple formats
repo = Repository("./my-project").analyze()
markdown = repo.to_markdown()
json_data = repo.to_json()
html_doc = repo.to_html()

# Example 4: Access raw data
data = repo.to_dict()
print(f"Files: {data['metadata']['file_count']}")
print(f"Languages: {list(data['statistics']['languages'].keys())}")
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

- File counts by type and language
- Code complexity scores
- Size metrics and distributions
- Language breakdown
- Project structure analysis

## 🤝 **Migration from v0.x**

The new version is backward compatible. Existing commands work unchanged:

```bash
# This still works exactly as before
src2md project -o docs.md --doc-pat '*.md' --src-pat '*.py'
```

New features are opt-in through additional flags and the Python API.

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.
