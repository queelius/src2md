"""
Context window management for optimizing code representation within token limits.
"""
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import tiktoken


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
        
        # TODO: Implement smart truncation that preserves structure
        # For now, do simple truncation
        return TokenCounter.truncate(content, target_tokens, self.model)
    
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