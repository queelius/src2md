# LLM-Powered Summarization API

## Overview

The LLM Summarizer module provides optional integration with Large Language Models (OpenAI and Anthropic) for intelligent, semantic code compression that preserves meaning while achieving aggressive compression ratios.

## Installation

LLM support requires optional dependencies:

```bash
# For OpenAI support
pip install src2md[openai]

# For Anthropic support
pip install src2md[anthropic]

# For all LLM providers
pip install src2md[llm]
```

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Optional
export OPENAI_API_BASE="https://api.openai.com/v1"  # Optional custom endpoint

# Anthropic Configuration
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_API_BASE="https://api.anthropic.com"  # Optional

# Default LLM Settings
export SRC2MD_LLM_PROVIDER="openai"  # or "anthropic"
export SRC2MD_LLM_MODEL="gpt-3.5-turbo"
export SRC2MD_LLM_MAX_TOKENS="500"
export SRC2MD_LLM_TEMPERATURE="0.3"
```

### `LLMProvider` (Enum)

Available LLM providers.

```python
from src2md.strategies.llm_summarizer import LLMProvider

LLMProvider.OPENAI     # OpenAI GPT models
LLMProvider.ANTHROPIC  # Anthropic Claude models
LLMProvider.NONE       # No LLM available (fallback)
```

### `LLMConfig`

Configuration for LLM-based summarization.

```python
from src2md.strategies.llm_summarizer import LLMConfig, LLMProvider

# Manual configuration
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    api_key="sk-...",  # Or use environment variable
    max_tokens=500,
    temperature=0.3,
    system_prompt="Custom prompt for summarization"
)

# Auto-detection from environment
config = LLMConfig()  # Automatically detects provider and API key

# Provider-specific models
openai_config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-3.5-turbo"  # or "gpt-4", "gpt-4-turbo"
)

anthropic_config = LLMConfig(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-haiku-20240307"  # or "claude-3-sonnet", "claude-3-opus"
)
```

## `LLMSummarizer` Class

The main class for LLM-powered summarization.

```python
from src2md.strategies.llm_summarizer import LLMSummarizer, LLMConfig

# Create summarizer with auto-detection
summarizer = LLMSummarizer()

# Create with specific configuration
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    max_tokens=750
)
summarizer = LLMSummarizer(config)

# Check if LLM is available
if summarizer.is_available():
    summary = summarizer.summarize_code(code_content, language="python")
else:
    # Fall back to rule-based summarization
    pass
```

## Core Methods

### `summarize_code()`

Summarize code with language-specific context.

```python
code = '''
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.logger = setup_logger()
    
    def process_batch(self, items):
        results = []
        for item in items:
            processed = self.transform(item)
            validated = self.validate(processed)
            if validated:
                results.append(self.finalize(validated))
        return results
    
    def transform(self, item):
        # Complex transformation logic
        # ... 50 lines of code
        return transformed
    
    def validate(self, item):
        # Validation logic
        # ... 30 lines of code
        return is_valid
    
    def finalize(self, item):
        # Finalization logic
        # ... 20 lines of code
        return final
'''

summary = summarizer.summarize_code(
    code=code,
    language="python",
    context="Data processing pipeline for ML features",
    target_tokens=200
)

# Output:
# class DataProcessor:
#     """Processes and validates data items in batches."""
#     
#     def __init__(self, config):
#         """Initialize with config, cache, and logger."""
#         ...
#     
#     def process_batch(self, items):
#         """Transform, validate, and finalize items.
#         Returns processed results list."""
#         ...
#     
#     # Core methods: transform(), validate(), finalize()
#     # Handles data transformation, validation rules, and finalization
```

### `summarize_chunk()`

Summarize a code chunk with context awareness.

```python
# For large files, process in chunks
chunks = split_into_chunks(large_file_content, chunk_size=2000)

summaries = []
for i, chunk in enumerate(chunks):
    summary = summarizer.summarize_chunk(
        chunk=chunk,
        file_path="src/processor.py",
        chunk_index=i,
        total_chunks=len(chunks),
        previous_context=summaries[-1] if summaries else None
    )
    summaries.append(summary)

final_summary = "\n".join(summaries)
```

### `summarize_with_importance()`

Importance-aware summarization.

```python
# Provide importance context for better summarization
summary = summarizer.summarize_with_importance(
    code=code,
    importance_score=0.9,  # High importance file
    file_type="api_endpoint",
    preserve_elements=["function_signatures", "error_handling", "api_routes"]
)
```

## Prompt Customization

### Default System Prompt

The default prompt optimizes for code understanding:

```python
DEFAULT_SYSTEM_PROMPT = """You are a code summarization expert. Your task is to create 
concise, informative summaries of code that preserve the most important information while 
significantly reducing the size. Focus on:

1. Public API signatures and their purpose
2. Core business logic and algorithms
3. Important data structures and their relationships
4. Key dependencies and external interactions
5. Critical error handling and edge cases

Omit:
- Implementation details that can be inferred
- Verbose comments that don't add value
- Repetitive code patterns
- Private helper methods unless critical

Your output should be valid code syntax with strategic use of '...' for omitted sections."""
```

### Custom Prompts

Create specialized prompts for different scenarios:

```python
# API documentation focus
api_prompt = """Summarize this code focusing on:
1. All public API endpoints and their parameters
2. Request/response schemas
3. Authentication requirements
4. Rate limiting and error codes
Maintain valid OpenAPI/Swagger compatibility where possible."""

config = LLMConfig(system_prompt=api_prompt)
summarizer = LLMSummarizer(config)

# Test code focus
test_prompt = """Summarize test code by:
1. Listing all test scenarios
2. Key assertions and expectations
3. Test data setup requirements
4. Coverage areas
Format as a concise test plan."""

# Security audit focus
security_prompt = """Analyze and summarize code for security:
1. Authentication/authorization logic
2. Input validation and sanitization
3. Cryptographic operations
4. External service interactions
5. Potential vulnerabilities
Preserve all security-critical code."""
```

## Integration with Repository

### Basic Integration

```python
from src2md import Repository

# Enable LLM summarization
repo = (Repository("./project")
    .with_summarization(
        compression_ratio=0.2,
        use_llm=True,
        llm_model="gpt-3.5-turbo"
    )
    .analyze())
```

### Advanced Configuration

```python
from src2md.strategies.llm_summarizer import LLMConfig

# Custom LLM configuration
llm_config = LLMConfig(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-haiku-20240307",
    max_tokens=300,
    temperature=0.2,
    system_prompt="Focus on algorithmic complexity and performance"
)

repo = (Repository("./project")
    .with_llm_config(llm_config)
    .with_summarization(use_llm=True)
    .analyze())
```

## Cost Optimization

### Token Usage Tracking

Monitor and control API costs:

```python
summarizer = LLMSummarizer()

# Track token usage
summary, tokens_used = summarizer.summarize_with_tracking(code)
print(f"Tokens used: {tokens_used}")
print(f"Estimated cost: ${summarizer.estimate_cost(tokens_used)}")

# Set token limits
summarizer.set_daily_limit(100_000)  # 100K tokens per day
summarizer.set_per_file_limit(1_000)  # 1K tokens per file
```

### Batch Processing

Optimize API calls with batching:

```python
# Process multiple files in a single API call
files = ["file1.py", "file2.py", "file3.py"]
contents = [read_file(f) for f in files]

summaries = summarizer.batch_summarize(
    contents=contents,
    file_paths=files,
    max_batch_size=5,  # Process 5 files at once
    total_token_budget=5000
)
```

### Caching

Reduce costs with intelligent caching:

```python
from src2md.strategies.llm_summarizer import CachedLLMSummarizer

# Enable caching
summarizer = CachedLLMSummarizer(
    cache_dir=".src2md_cache",
    cache_ttl=86400  # 24 hours
)

# First call hits API
summary1 = summarizer.summarize_code(code)

# Subsequent calls use cache
summary2 = summarizer.summarize_code(code)  # From cache, no API call
```

## Model Selection Guide

### OpenAI Models

| Model | Best For | Max Tokens | Cost |
|-------|----------|------------|------|
| gpt-3.5-turbo | Fast, general summarization | 4K | $ |
| gpt-4 | Complex code understanding | 8K | $$ |
| gpt-4-turbo | Large files, better context | 128K | $$$ |

### Anthropic Models

| Model | Best For | Max Tokens | Cost |
|-------|----------|------------|------|
| claude-3-haiku | Fast, efficient summarization | 200K | $ |
| claude-3-sonnet | Balanced quality/speed | 200K | $$ |
| claude-3-opus | Highest quality analysis | 200K | $$$ |

### Selection Strategy

```python
def select_model(file_size: int, importance: float, budget: str) -> str:
    """Select optimal model based on context."""
    if budget == "low":
        return "gpt-3.5-turbo" if file_size < 4000 else "claude-3-haiku"
    elif budget == "medium":
        return "gpt-4" if importance > 0.8 else "gpt-3.5-turbo"
    else:  # high budget
        return "gpt-4-turbo" if file_size > 8000 else "claude-3-sonnet"
```

## Error Handling

### Graceful Fallbacks

```python
from src2md.strategies.summarization import SummarizationStrategy

def smart_summarize(code: str, file_path: str) -> str:
    """Summarize with automatic fallback."""
    try:
        # Try LLM summarization first
        llm_summarizer = LLMSummarizer()
        if llm_summarizer.is_available():
            return llm_summarizer.summarize_code(code)
    except Exception as e:
        logger.warning(f"LLM summarization failed: {e}")
    
    # Fall back to AST-based summarization
    try:
        strategy = SummarizationStrategy()
        return strategy.summarize(Path(file_path), code)
    except Exception as e:
        logger.error(f"AST summarization failed: {e}")
    
    # Final fallback: simple truncation
    return code[:1000] + "\n# ... truncated"
```

### API Error Handling

```python
from src2md.strategies.llm_summarizer import (
    RateLimitError,
    APIKeyError,
    ModelNotAvailableError
)

try:
    summary = summarizer.summarize_code(code)
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
    summary = summarizer.summarize_code(code)
except APIKeyError:
    print("Invalid API key. Check your configuration.")
    # Fall back to non-LLM summarization
except ModelNotAvailableError as e:
    print(f"Model {e.model} not available. Using fallback.")
    # Use alternative model
```

## Best Practices

### 1. Start with Lower-Cost Models

Test with cheaper models first:

```python
# Development: Use fast, cheap model
dev_config = LLMConfig(model="gpt-3.5-turbo", max_tokens=300)

# Production: Use better model for important files
prod_config = LLMConfig(model="gpt-4", max_tokens=500)
```

### 2. Implement Progressive Summarization

More aggressive compression for less important files:

```python
def progressive_summarize(file_path: str, content: str, importance: float):
    if importance > 0.9:
        # No LLM needed for critical files
        return content
    elif importance > 0.5:
        # Light summarization
        return summarizer.summarize_code(content, target_tokens=500)
    else:
        # Heavy summarization
        return summarizer.summarize_code(content, target_tokens=200)
```

### 3. Cache Aggressively

Implement multi-level caching:

```python
# Memory cache for session
memory_cache = {}

# Disk cache for persistence
disk_cache = DiskCache(".cache")

def cached_summarize(content_hash: str, content: str):
    # Check memory cache
    if content_hash in memory_cache:
        return memory_cache[content_hash]
    
    # Check disk cache
    if cached := disk_cache.get(content_hash):
        memory_cache[content_hash] = cached
        return cached
    
    # Generate summary
    summary = summarizer.summarize_code(content)
    
    # Update caches
    memory_cache[content_hash] = summary
    disk_cache.set(content_hash, summary)
    
    return summary
```

### 4. Monitor Quality

Track summarization quality metrics:

```python
def evaluate_summary(original: str, summary: str) -> dict:
    return {
        "compression_ratio": len(summary) / len(original),
        "functions_preserved": count_functions(summary) / count_functions(original),
        "imports_preserved": all(imp in summary for imp in extract_imports(original)),
        "syntax_valid": is_valid_syntax(summary)
    }

# Log quality metrics
metrics = evaluate_summary(original_code, summary)
logger.info(f"Summarization metrics: {metrics}")
```

## See Also

- [Summarization API](./summarization.md) - AST-based summarization strategies
- [Context API](./context.md) - Context window management
- [Repository API](./repository.md) - Repository analysis and integration