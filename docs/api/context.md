# Context Window Management API

## Overview

The context window management module provides intelligent optimization of code repositories to fit within LLM token limits while preserving the most important information.

## Core Classes

### `ContextWindow` (Enum)

Predefined context window sizes for common LLMs.

```python
from src2md.core.context import ContextWindow

# Available windows:
ContextWindow.GPT_35      # 16,385 tokens (GPT-3.5 16K)
ContextWindow.GPT_4       # 128,000 tokens (GPT-4 128K) 
ContextWindow.GPT_4_32K   # 32,768 tokens (GPT-4 32K)
ContextWindow.CLAUDE_2    # 100,000 tokens (Claude 2)
ContextWindow.CLAUDE_3    # 200,000 tokens (Claude 3)
ContextWindow.LLAMA_2     # 4,096 tokens (Llama 2)
ContextWindow.CUSTOM      # User-defined limit
```

### `TokenBudget`

Manages token allocation across different content types.

```python
from src2md.core.context import TokenBudget

# Create a token budget
budget = TokenBudget(total=100_000)

# Allocate tokens for different categories
budget.allocate("core_files", 50_000)
budget.allocate("tests", 20_000)
budget.allocate("documentation", 10_000)

# Check remaining tokens
remaining = budget.remaining  # 20,000

# Consume tokens as you process files
budget.consume(15_000)  # Returns True if successful

# Get allocation ratios
ratios = budget.get_allocation_ratio()
# {'core_files': 0.5, 'tests': 0.2, 'documentation': 0.1, 'consumed': 0.15}
```

### `TokenCounter`

Accurate token counting using tiktoken for different model encodings.

```python
from src2md.core.context import TokenCounter

# Count tokens for a specific model
text = "Your code content here..."
tokens = TokenCounter.count(text, model="gpt-4")

# Batch count multiple texts
texts = ["file1 content", "file2 content", "file3 content"]
total = TokenCounter.count_batch(texts, model="claude-3")

# Estimate tokens (faster, less accurate)
estimated = TokenCounter.estimate(text)  # Uses character-based estimation
```

### `ContextOptimizer`

The main class for optimizing code to fit within context windows.

```python
from src2md.core.context import ContextOptimizer, ContextWindow
from src2md.core.repository import FileEntry

# Create optimizer
optimizer = ContextOptimizer(
    context_window=ContextWindow.GPT_4,
    preserve_structure=True,
    aggressive_mode=False
)

# Optimize a list of files
files = [FileEntry(...), FileEntry(...), ...]
optimized = optimizer.optimize(
    files,
    importance_scores={'file1.py': 0.9, 'file2.py': 0.5}
)

# Smart truncation preserves code structure
truncated = optimizer.smart_truncate(
    content="...",
    target_tokens=1000,
    file_type="python"
)
```

## Smart Truncation Features

The `ContextOptimizer` includes intelligent truncation that preserves code structure:

### 1. Structure-Aware Truncation

```python
# Original code (too long)
class MyClass:
    def method1(self):
        # 100 lines of code
        pass
    
    def method2(self):
        # 50 lines of code
        pass
    
    def method3(self):
        # 75 lines of code
        pass

# Smart truncation preserves complete methods
class MyClass:
    def method1(self):
        # 100 lines of code
        pass
    
    def method2(self):
        # 50 lines of code
        pass
    
    # ... truncated (method3 removed completely)
```

### 2. Priority Preservation

- Preserves imports and module-level docstrings
- Keeps public API methods over private ones
- Maintains class hierarchy and relationships
- Preserves type hints and function signatures

### 3. Syntax Validity

The truncation always produces syntactically valid code:

```python
# Never cuts in the middle of blocks
# Never leaves unclosed brackets or quotes
# Adds ellipsis comments to indicate truncation
```

## Integration with Repository

The context optimization integrates seamlessly with the Repository fluent API:

```python
from src2md import Repository, ContextWindow

# Automatic optimization
repo = (Repository("./project")
    .optimize_for(ContextWindow.GPT_4)
    .analyze())

# Custom token limit
repo = (Repository("./project")
    .optimize_for_tokens(50_000)
    .analyze())

# With importance scoring
repo = (Repository("./project")
    .with_importance_scoring()
    .prioritize(["src/core/", "api/"])
    .optimize_for(ContextWindow.CLAUDE_3)
    .analyze())
```

## Configuration Options

### Optimization Strategies

```python
# Conservative: Preserve as much as possible
optimizer = ContextOptimizer(
    context_window=ContextWindow.GPT_4,
    aggressive_mode=False,
    preserve_structure=True,
    min_chunk_size=100  # Don't create tiny fragments
)

# Aggressive: Maximum compression
optimizer = ContextOptimizer(
    context_window=ContextWindow.GPT_35,
    aggressive_mode=True,
    preserve_structure=False,
    min_chunk_size=50
)
```

### Custom Windows

```python
# Define custom context window
optimizer = ContextOptimizer(
    context_window=ContextWindow.CUSTOM,
    custom_limit=75_000,  # 75K tokens
    model="gpt-4"  # For token counting
)
```

## Best Practices

### 1. Use Importance Scoring

Always enable importance scoring for better file prioritization:

```python
repo = Repository("./project").with_importance_scoring()
```

### 2. Prioritize Critical Paths

Explicitly mark important directories:

```python
repo = repo.prioritize(["src/api/", "src/core/", "src/models/"])
```

### 3. Combine with Summarization

Use summarization for even better compression:

```python
repo = (repo
    .with_summarization(compression_ratio=0.3)
    .optimize_for(ContextWindow.GPT_4))
```

### 4. Monitor Token Usage

Check actual token usage after optimization:

```python
data = repo.to_dict()
print(f"Total tokens: {data['metadata'].get('total_tokens', 0)}")
print(f"Token limit: {data['metadata'].get('token_limit', 0)}")
print(f"Utilization: {data['metadata'].get('token_utilization', 0):.1%}")
```

## Error Handling

The context optimizer handles various edge cases:

```python
try:
    optimized = optimizer.optimize(files)
except TokenLimitExceeded as e:
    print(f"Cannot fit within {e.limit} tokens even with maximum compression")
except InvalidEncoding as e:
    print(f"Failed to count tokens: {e.message}")
```

## Performance Considerations

- **Token Counting**: Uses cached encoders for efficiency
- **Batch Processing**: Process multiple files together for better performance
- **Estimation Mode**: Use `estimate_tokens=True` for faster, less accurate counting
- **Streaming**: Large repositories can use streaming mode (coming soon)

## See Also

- [Summarization API](./summarization.md) - Code summarization strategies
- [Repository API](./repository.md) - Repository analysis and fluent API
- [LLM Summarizer API](./llm_summarizer.md) - LLM-powered summarization