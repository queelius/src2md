# Changelog

All notable changes to src2md will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-03

### 🚀 Major Release - Complete Architecture Redesign

This release introduces a completely redesigned architecture with intelligent context window optimization for LLMs, a fluent API, and sophisticated file importance scoring.

### Added
- **Fluent API** for elegant method chaining
  ```python
  Repository("/path").optimize_for(ContextWindow.GPT_4).analyze().to_markdown()
  ```
- **Context Window Management** with predefined windows for popular LLMs (GPT-4, Claude, etc.)
- **Intelligent File Importance Scoring** based on multiple factors:
  - Entrypoint detection
  - Export/import analysis
  - Code complexity
  - Documentation quality
  - File recency
- **Token Counting** with tiktoken for accurate context optimization
- **Progressive Summarization** to fit large codebases into token limits
- **Multi-Repository Support** (foundation laid for future releases)
- **New Formatters Architecture** with streaming support
- **Comprehensive Test Suite** with 90+ unit and integration tests

### Changed
- Complete rewrite of core architecture
- Moved from functional to object-oriented design
- Replaced dirschema dependency with native implementation
- Improved output formats with better structure
- Enhanced statistics with context window usage

### Improved
- Performance optimizations for large codebases
- Better memory management with streaming formatters
- More accurate language detection
- Smarter file filtering with priority paths

### Breaking Changes
- API completely changed from v1.x
- Old functional API (`analyze_codebase()`) moved to legacy module
- New import structure: `from src2md import Repository, ContextWindow`

### Migration Guide
```python
# Old (v1.x)
from src2md import analyze_codebase, to_markdown
data = analyze_codebase("/path")
output = to_markdown(data)

# New (v2.0)
from src2md import Repository
output = Repository("/path").analyze().to_markdown()
```

## [1.0.0] - Previous Release

### Added
- Initial implementation with basic markdown generation
- Support for multiple output formats (JSON, JSONL, Markdown, HTML)
- Basic file filtering with patterns
- Simple statistics generation