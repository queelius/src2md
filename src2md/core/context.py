"""
Context window management for optimizing code representation within token limits.
"""
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import tiktoken
import re


class ContextWindow(Enum):
    """Predefined context window sizes for common LLMs."""
    GPT_35 = 16_385  # GPT-3.5 16K
    GPT_4 = 128_000  # GPT-4 128K
    GPT_4_32K = 32_768  # GPT-4 32K
    CLAUDE_2 = 100_000  # Claude 2 100K
    CLAUDE_3 = 200_000  # Claude 3 200K
    LLAMA_2 = 4_096  # Llama 2 4K
    CUSTOM = 0  # User-defined


@dataclass
class TokenBudget:
    """Manages token allocation across different content types."""
    total: int
    used: int = 0
    reserved: Dict[str, int] = None
    
    def __post_init__(self):
        if self.reserved is None:
            self.reserved = {}
    
    @property
    def remaining(self) -> int:
        """Calculate remaining tokens."""
        return self.total - self.used - sum(self.reserved.values())
    
    def allocate(self, category: str, tokens: int) -> bool:
        """Try to allocate tokens for a category."""
        if tokens <= self.remaining:
            self.reserved[category] = self.reserved.get(category, 0) + tokens
            return True
        return False
    
    def consume(self, tokens: int) -> bool:
        """Consume tokens from the budget."""
        if tokens <= self.remaining:
            self.used += tokens
            return True
        return False
    
    def get_allocation_ratio(self) -> Dict[str, float]:
        """Get the ratio of tokens allocated to each category."""
        total_allocated = sum(self.reserved.values()) + self.used
        if total_allocated == 0:
            return {}
        
        ratios = {
            category: amount / total_allocated 
            for category, amount in self.reserved.items()
        }
        ratios['consumed'] = self.used / total_allocated
        return ratios


class TokenCounter:
    """Count tokens for different encodings."""
    
    # Cache encoders to avoid re-initialization
    _encoders = {}
    
    @classmethod
    def get_encoder(cls, model: str = "gpt-4"):
        """Get or create a tiktoken encoder for the model."""
        if model not in cls._encoders:
            try:
                # Try to get encoding for specific model
                cls._encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fall back to cl100k_base (GPT-4 default)
                cls._encoders[model] = tiktoken.get_encoding("cl100k_base")
        return cls._encoders[model]
    
    @classmethod
    def count(cls, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text for the specified model."""
        encoder = cls.get_encoder(model)
        return len(encoder.encode(text))
    
    @classmethod
    def truncate(cls, text: str, max_tokens: int, model: str = "gpt-4") -> str:
        """Truncate text to fit within token limit."""
        encoder = cls.get_encoder(model)
        tokens = encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return encoder.decode(truncated_tokens)
    
    @classmethod
    def split_into_chunks(cls, text: str, chunk_size: int, 
                         overlap: int = 0, model: str = "gpt-4") -> List[str]:
        """Split text into chunks of specified token size with optional overlap."""
        encoder = cls.get_encoder(model)
        tokens = encoder.encode(text)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(encoder.decode(chunk_tokens))
            
            # Move start position considering overlap
            start = end - overlap if overlap > 0 else end
            
        return chunks


class ContextOptimizer:
    """Optimize content to fit within context windows."""
    
    def __init__(self, window: ContextWindow = ContextWindow.GPT_4, 
                 model: str = "gpt-4"):
        """Initialize with a context window size."""
        if window == ContextWindow.CUSTOM:
            raise ValueError("Use ContextOptimizer.with_limit() for custom limits")
        
        self.window = window
        self.limit = window.value
        self.model = model
        self.budget = TokenBudget(total=self.limit)
    
    @classmethod
    def with_limit(cls, limit: int, model: str = "gpt-4"):
        """Create optimizer with custom token limit."""
        optimizer = cls.__new__(cls)
        optimizer.window = ContextWindow.CUSTOM
        optimizer.limit = limit
        optimizer.model = model
        optimizer.budget = TokenBudget(total=limit)
        return optimizer
    
    def can_fit(self, content: str) -> bool:
        """Check if content fits within remaining budget."""
        tokens = TokenCounter.count(content, self.model)
        return tokens <= self.budget.remaining
    
    def add_content(self, content: str, category: str = "general") -> Tuple[bool, int]:
        """
        Try to add content to the context.
        
        Returns:
            Tuple of (success, tokens_used)
        """
        tokens = TokenCounter.count(content, self.model)
        
        if self.budget.consume(tokens):
            return True, tokens
        return False, 0
    
    def allocate_budget(self, allocations: Dict[str, float]) -> Dict[str, int]:
        """
        Allocate token budget based on percentages.
        
        Args:
            allocations: Dict mapping categories to percentage (0.0-1.0)
            
        Returns:
            Dict mapping categories to token counts
        """
        if abs(sum(allocations.values()) - 1.0) > 0.01:
            raise ValueError("Allocations must sum to 1.0")
        
        token_allocations = {}
        remaining = self.limit
        
        # Sort by allocation size to handle rounding better
        sorted_allocs = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
        
        for i, (category, percentage) in enumerate(sorted_allocs):
            if i == len(sorted_allocs) - 1:
                # Give remaining tokens to last category to handle rounding
                tokens = remaining
            else:
                tokens = int(self.limit * percentage)
                remaining -= tokens
            
            token_allocations[category] = tokens
            self.budget.allocate(category, tokens)
        
        return token_allocations
    
    def optimize_content(self, content: str, target_tokens: int,
                        preserve_structure: bool = True) -> str:
        """
        Optimize content to fit within target token count.
        
        Args:
            content: Content to optimize
            target_tokens: Target token count
            preserve_structure: Try to preserve code structure
            
        Returns:
            Optimized content
        """
        current_tokens = TokenCounter.count(content, self.model)
        
        if current_tokens <= target_tokens:
            return content
        
        if not preserve_structure:
            # Simple truncation
            return TokenCounter.truncate(content, target_tokens, self.model)
        
        # Smart truncation that preserves structure
        return self._smart_truncate(content, target_tokens)
    
    def _smart_truncate(self, content: str, target_tokens: int) -> str:
        """
        Smart truncation that attempts to preserve code structure.
        
        Strategy:
        1. Try to keep complete functions/classes
        2. Preserve imports and module-level docstrings
        3. Remove comments and docstrings from functions if needed
        4. Truncate at logical boundaries (end of functions, classes)
        """
        lines = content.splitlines()
        
        # Identify structural boundaries
        structure_markers = []
        indent_stack = [0]
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if not stripped:
                continue
            
            indent = len(line) - len(stripped)
            
            # Track class and function definitions
            if re.match(r'^(class|def|async def)\s+', stripped):
                structure_markers.append({
                    'line': i,
                    'indent': indent,
                    'type': 'definition',
                    'content': line
                })
                indent_stack.append(indent)
            elif indent <= indent_stack[-1] and indent_stack[-1] > 0:
                # End of a code block
                while indent_stack and indent_stack[-1] > indent:
                    indent_stack.pop()
                structure_markers.append({
                    'line': i,
                    'indent': indent,
                    'type': 'boundary'
                })
        
        # Progressive truncation strategy
        result_lines = []
        current_tokens = 0
        
        # Phase 1: Keep imports and module docstrings
        in_module_docstring = False
        for i, line in enumerate(lines):
            if i < min(50, len(lines)):  # Check first 50 lines for imports
                if re.match(r'^(from .* import|import )', line):
                    result_lines.append(line)
                elif i < 3 and '"""' in line:
                    in_module_docstring = True
                    result_lines.append(line)
                elif in_module_docstring:
                    result_lines.append(line)
                    if '"""' in line and i > 0:
                        in_module_docstring = False
                        break
        
        # Phase 2: Add complete structural units until we approach the limit
        current_tokens = TokenCounter.count('\n'.join(result_lines), self.model)
        
        if current_tokens < target_tokens:
            # Find structural units (functions/classes)
            units = []
            current_unit = []
            current_indent = 0
            
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                
                if re.match(r'^(class|def|async def)\s+', stripped) and indent == 0:
                    if current_unit:
                        units.append(current_unit)
                    current_unit = [line]
                    current_indent = indent
                elif current_unit:
                    if indent > current_indent or not stripped:
                        current_unit.append(line)
                    else:
                        units.append(current_unit)
                        current_unit = [line] if re.match(r'^(class|def|async def)\s+', stripped) else []
            
            if current_unit:
                units.append(current_unit)
            
            # Add units until we approach the limit
            for unit in units:
                unit_text = '\n'.join(unit)
                unit_tokens = TokenCounter.count(unit_text, self.model)
                
                if current_tokens + unit_tokens <= target_tokens * 0.95:  # Leave 5% buffer
                    result_lines.extend(unit)
                    current_tokens += unit_tokens
                else:
                    # Try to add a summarized version
                    summary = self._summarize_unit(unit)
                    summary_tokens = TokenCounter.count(summary, self.model)
                    if current_tokens + summary_tokens <= target_tokens:
                        result_lines.append(summary)
                        current_tokens += summary_tokens
                    else:
                        break
        
        result = '\n'.join(result_lines)
        
        # Final check and hard truncation if needed
        if TokenCounter.count(result, self.model) > target_tokens:
            result = TokenCounter.truncate(result, target_tokens, self.model)
        
        return result
    
    def _summarize_unit(self, unit_lines: List[str]) -> str:
        """Create a summary of a code unit (function/class)."""
        if not unit_lines:
            return ""
        
        first_line = unit_lines[0].strip()
        
        # Extract function/class signature
        if first_line.startswith(('def ', 'async def ', 'class ')):
            # Keep just the signature
            signature = first_line
            if not signature.endswith(':'):
                signature += ':'
            return f"{signature}\n    ..."
        
        return f"# ... ({len(unit_lines)} lines omitted)"
    
    def get_summary(self) -> Dict:
        """Get summary of context window usage."""
        return {
            'window': self.window.name,
            'limit': self.limit,
            'used': self.budget.used,
            'remaining': self.budget.remaining,
            'utilization': self.budget.used / self.limit,
            'allocations': self.budget.get_allocation_ratio()
        }