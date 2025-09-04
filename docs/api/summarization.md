# Summarization Strategies API

## Overview

The summarization module provides intelligent code compression strategies using AST analysis, language-specific patterns, and optional LLM integration to reduce code size while preserving critical information.

## Core Components

### `SummarizationLevel` (Enum)

Defines the level of detail for summarization.

```python
from src2md.strategies.summarization import SummarizationLevel

SummarizationLevel.FULL        # No summarization
SummarizationLevel.SIGNATURES  # Function/class signatures only
SummarizationLevel.DOCSTRINGS  # Signatures + docstrings
SummarizationLevel.OUTLINE     # High-level structure only
SummarizationLevel.MINIMAL     # Bare minimum information
```

### `SummarizationConfig`

Configuration for summarization behavior.

```python
from src2md.strategies.summarization import SummarizationConfig, SummarizationLevel

config = SummarizationConfig(
    level=SummarizationLevel.DOCSTRINGS,
    preserve_imports=True,      # Keep import statements
    preserve_exports=True,      # Keep export declarations
    preserve_docstrings=True,   # Keep documentation
    preserve_comments=False,    # Remove inline comments
    max_line_length=120,        # Line wrap limit
    target_compression_ratio=0.3  # Target 30% of original size
)
```

## Language-Specific Summarizers

### `PythonSummarizer`

AST-based Python code summarization with multiple compression levels.

```python
from src2md.strategies.summarization import PythonSummarizer, SummarizationConfig

# Create summarizer with custom config
config = SummarizationConfig(
    level=SummarizationLevel.DOCSTRINGS,
    preserve_imports=True
)
summarizer = PythonSummarizer(config)

# Summarize Python code
python_code = '''
import numpy as np
from typing import List, Dict

class DataProcessor:
    """Processes data for machine learning."""
    
    def __init__(self, config: Dict):
        """Initialize with configuration."""
        self.config = config
        self._cache = {}
    
    def process(self, data: List) -> np.ndarray:
        """Process raw data into features."""
        # Complex implementation
        result = self._transform(data)
        result = self._normalize(result)
        return result
    
    def _transform(self, data):
        # Private method implementation
        pass
'''

summary = summarizer.summarize(python_code)
# Output preserves structure and docstrings:
# import numpy as np
# from typing import List, Dict
#
# class DataProcessor:
#     """Processes data for machine learning."""
#     
#     def __init__(self, config: Dict):
#         """Initialize with configuration."""
#         ...
#     
#     def process(self, data: List) -> np.ndarray:
#         """Process raw data into features."""
#         ...
```

#### Summarization Levels for Python

**MINIMAL**: Only class and function names
```python
class DataProcessor:
    def __init__(self, ...): ...
    def process(self, ...): ...
```

**OUTLINE**: Structure with type hints
```python
class DataProcessor:
    def __init__(self, config: Dict): ...
    def process(self, data: List) -> np.ndarray: ...
```

**DOCSTRINGS**: Includes documentation
```python
class DataProcessor:
    """Processes data for machine learning."""
    def __init__(self, config: Dict):
        """Initialize with configuration."""
        ...
```

**SIGNATURES**: Full signatures with defaults
```python
class DataProcessor:
    """Processes data for machine learning."""
    def __init__(self, config: Dict, cache_size: int = 100):
        """Initialize with configuration."""
        ...
```

### `JavaScriptSummarizer`

Handles JavaScript and TypeScript files with ES6+ syntax support.

```python
from src2md.strategies.summarization import JavaScriptSummarizer

summarizer = JavaScriptSummarizer()

js_code = '''
import React from 'react';
import { useState, useEffect } from 'react';

export const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="profile">
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  );
};

const fetchUser = async (id) => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};
'''

summary = summarizer.summarize(js_code)
# Preserves component structure and exports
```

### `TestSummarizer`

Specialized for test files, extracting test names and assertions.

```python
from src2md.strategies.summarization import TestSummarizer

summarizer = TestSummarizer()

test_code = '''
import pytest
from myapp import Calculator

class TestCalculator:
    def test_addition(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5
        assert calc.add(-1, 1) == 0
        assert calc.add(0, 0) == 0
    
    def test_multiplication(self):
        calc = Calculator()
        assert calc.multiply(3, 4) == 12
        assert calc.multiply(-2, 3) == -6
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 1),
        (2, 3, 6),
        (0, 5, 0),
    ])
    def test_multiply_parametrized(self, a, b, expected):
        calc = Calculator()
        assert calc.multiply(a, b) == expected
'''

summary = summarizer.summarize(test_code)
# Output:
# Tests for Calculator:
# - test_addition: Tests add() with positive, negative, zero
# - test_multiplication: Tests multiply() with various inputs
# - test_multiply_parametrized: Parametrized tests for multiply()
```

### `JSONSummarizer`

Extracts schema and sample data from JSON files.

```python
from src2md.strategies.summarization import JSONSummarizer

summarizer = JSONSummarizer()

json_data = '''
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    ... // 100 more users
  ],
  "settings": {
    "theme": "dark",
    "notifications": true,
    "language": "en"
  }
}
'''

summary = summarizer.summarize(json_data)
# Output:
# {
#   "users": [
#     {"id": "number", "name": "string", "email": "string", "role": "string"}
#   ],
#   "settings": {
#     "theme": "string",
#     "notifications": "boolean",
#     "language": "string"
#   }
# }
```

### `YAMLSummarizer`

Handles YAML configuration files with schema extraction.

```python
from src2md.strategies.summarization import YAMLSummarizer

summarizer = YAMLSummarizer()

yaml_content = '''
database:
  host: localhost
  port: 5432
  name: myapp
  credentials:
    username: dbuser
    password: secret

cache:
  provider: redis
  ttl: 3600
  
features:
  - authentication
  - notifications
  - analytics
'''

summary = summarizer.summarize(yaml_content)
# Preserves structure with value types
```

## `SummarizationStrategy` (Main Class)

The main strategy class that orchestrates different summarizers.

```python
from src2md.strategies.summarization import SummarizationStrategy, SummarizationConfig
from pathlib import Path

# Create strategy with configuration
config = SummarizationConfig(
    level=SummarizationLevel.DOCSTRINGS,
    target_compression_ratio=0.3
)
strategy = SummarizationStrategy(config)

# Register custom summarizers
strategy.register_summarizer(MyCustomSummarizer())

# Summarize a file
file_path = Path("src/main.py")
content = file_path.read_text()
summary = strategy.summarize(file_path, content, target_ratio=0.2)

# Check if summarization is needed
should_summarize = strategy.should_summarize(
    file_path=file_path,
    importance_score=0.7,
    size_bytes=10000
)

# Estimate compression ratio
estimated_ratio = strategy.estimate_compression(file_path, content)
```

## Integration with Repository

The summarization integrates seamlessly with the Repository API:

```python
from src2md import Repository

# Enable summarization
repo = (Repository("./project")
    .with_summarization(
        compression_ratio=0.3,
        preserve_important=True,
        use_llm=False
    )
    .analyze())

# Selective summarization
repo = (Repository("./project")
    .summarize_tests()      # Only summarize test files
    .summarize_docs()       # Only summarize documentation
    .analyze())

# Custom summarization config
from src2md.strategies.summarization import SummarizationConfig, SummarizationLevel

config = SummarizationConfig(
    level=SummarizationLevel.MINIMAL,
    preserve_imports=True,
    target_compression_ratio=0.1  # Aggressive 10% compression
)

repo = (Repository("./project")
    .with_summarization_config(config)
    .analyze())
```

## Advanced Features

### Custom Summarizers

Create custom summarizers for specific file types:

```python
from src2md.strategies.summarization import CodeSummarizer
from pathlib import Path

class SQLSummarizer(CodeSummarizer):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix in {'.sql', '.ddl'}
    
    def summarize(self, content: str, **kwargs) -> str:
        # Extract table definitions and key queries
        tables = self.extract_tables(content)
        views = self.extract_views(content)
        procedures = self.extract_procedures(content)
        
        return f"""
        -- Tables: {', '.join(tables)}
        -- Views: {', '.join(views)}
        -- Procedures: {', '.join(procedures)}
        
        {self.extract_schema(content)}
        """

# Register custom summarizer
strategy = SummarizationStrategy()
strategy.register_summarizer(SQLSummarizer())
```

### Compression Ratio Control

Fine-tune compression based on file importance:

```python
def adaptive_compression(file_path: Path, importance: float) -> float:
    """Calculate compression ratio based on importance."""
    if importance > 0.9:
        return 1.0  # No compression for critical files
    elif importance > 0.7:
        return 0.5  # Light compression
    elif importance > 0.4:
        return 0.3  # Moderate compression
    else:
        return 0.1  # Heavy compression

# Apply adaptive compression
for file in files:
    ratio = adaptive_compression(file.path, file.importance)
    summary = strategy.summarize(file.path, file.content, target_ratio=ratio)
```

### Batch Processing

Process multiple files efficiently:

```python
from concurrent.futures import ThreadPoolExecutor

def summarize_batch(files: List[FileEntry]) -> List[str]:
    strategy = SummarizationStrategy()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(strategy.summarize, f.path, f.content)
            for f in files
        ]
        return [f.result() for f in futures]
```

## Performance Optimization

### AST Caching

The Python summarizer caches AST parsing for efficiency:

```python
summarizer = PythonSummarizer()
summarizer.enable_cache()  # Cache parsed ASTs

# Process multiple files with same imports
for file in python_files:
    summary = summarizer.summarize(file.content)  # Reuses cached AST info
```

### Streaming Summarization

For large files, use streaming mode:

```python
def stream_summarize(file_path: Path, chunk_size: int = 10000):
    strategy = SummarizationStrategy()
    
    with open(file_path, 'r') as f:
        while chunk := f.read(chunk_size):
            yield strategy.summarize_chunk(chunk)
```

## Best Practices

### 1. Choose Appropriate Levels

Match summarization level to use case:

- **MINIMAL**: Quick overview, maximum compression
- **OUTLINE**: Code structure analysis
- **DOCSTRINGS**: API documentation
- **SIGNATURES**: Type checking and validation
- **FULL**: Critical files that shouldn't be compressed

### 2. Preserve Important Files

Always preserve critical files:

```python
repo = repo.with_summarization(preserve_important=True)
```

### 3. Test Summarization Quality

Validate summarization doesn't lose critical information:

```python
original = file_content
summary = strategy.summarize(path, original)
assert "critical_function" in summary  # Ensure key elements preserved
assert len(summary) < len(original) * 0.5  # Verify compression
```

### 4. Monitor Compression Metrics

Track summarization effectiveness:

```python
data = repo.to_dict()
for file in data['source_files']:
    if file.get('was_summarized'):
        ratio = file['size'] / file['original_size']
        print(f"{file['path']}: {ratio:.1%} compression")
```

## Error Handling

Handle summarization failures gracefully:

```python
try:
    summary = strategy.summarize(file_path, content)
except SyntaxError as e:
    # Fall back to simple truncation for invalid syntax
    summary = content[:1000] + "\n# ... truncated due to syntax error"
except Exception as e:
    # Log error and return original
    logger.error(f"Summarization failed for {file_path}: {e}")
    summary = content
```

## See Also

- [LLM Summarizer API](./llm_summarizer.md) - LLM-powered summarization
- [Context API](./context.md) - Context window management
- [Repository API](./repository.md) - Repository analysis