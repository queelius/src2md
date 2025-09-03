"""
Unit tests for context window management.
"""
import pytest
from src2md.core.context import (
    ContextWindow, TokenBudget, TokenCounter, ContextOptimizer
)


class TestContextWindow:
    """Test ContextWindow enum."""
    
    def test_predefined_windows(self):
        """Test predefined context window sizes."""
        assert ContextWindow.GPT_35.value == 16_385
        assert ContextWindow.GPT_4.value == 128_000
        assert ContextWindow.GPT_4_32K.value == 32_768
        assert ContextWindow.CLAUDE_2.value == 100_000
        assert ContextWindow.CLAUDE_3.value == 200_000
        assert ContextWindow.LLAMA_2.value == 4_096
        assert ContextWindow.CUSTOM.value == 0


class TestTokenBudget:
    """Test TokenBudget class."""
    
    def test_initialization(self):
        """Test budget initialization."""
        budget = TokenBudget(total=1000)
        assert budget.total == 1000
        assert budget.used == 0
        assert budget.remaining == 1000
        assert budget.reserved == {}
    
    def test_allocation(self):
        """Test token allocation."""
        budget = TokenBudget(total=1000)
        
        # Successful allocation
        assert budget.allocate("category1", 300) is True
        assert budget.remaining == 700
        assert budget.reserved["category1"] == 300
        
        # Another allocation
        assert budget.allocate("category2", 400) is True
        assert budget.remaining == 300
        
        # Allocation exceeding remaining
        assert budget.allocate("category3", 500) is False
        assert budget.remaining == 300
    
    def test_consumption(self):
        """Test token consumption."""
        budget = TokenBudget(total=1000)
        
        # Consume tokens
        assert budget.consume(200) is True
        assert budget.used == 200
        assert budget.remaining == 800
        
        # Consume more
        assert budget.consume(300) is True
        assert budget.used == 500
        assert budget.remaining == 500
        
        # Try to consume more than remaining
        assert budget.consume(600) is False
        assert budget.used == 500
    
    def test_mixed_allocation_and_consumption(self):
        """Test mixed allocation and consumption."""
        budget = TokenBudget(total=1000)
        
        # Allocate some
        budget.allocate("docs", 300)
        assert budget.remaining == 700
        
        # Consume some
        budget.consume(400)
        assert budget.remaining == 300
        assert budget.used == 400
        
        # Try to allocate more than remaining
        assert budget.allocate("code", 400) is False
        
        # Can still allocate within remaining
        assert budget.allocate("code", 200) is True
        assert budget.remaining == 100
    
    def test_allocation_ratio(self):
        """Test allocation ratio calculation."""
        budget = TokenBudget(total=1000)
        
        budget.allocate("category1", 300)
        budget.allocate("category2", 200)
        budget.consume(500)
        
        ratios = budget.get_allocation_ratio()
        assert ratios["category1"] == 0.3  # 300/1000
        assert ratios["category2"] == 0.2  # 200/1000
        assert ratios["consumed"] == 0.5   # 500/1000


class TestTokenCounter:
    """Test TokenCounter class."""
    
    @pytest.mark.requires_tiktoken
    def test_get_encoder(self):
        """Test encoder retrieval."""
        encoder1 = TokenCounter.get_encoder("gpt-4")
        encoder2 = TokenCounter.get_encoder("gpt-4")
        
        # Should return cached encoder
        assert encoder1 is encoder2
        
        # Different model should get different encoder
        encoder3 = TokenCounter.get_encoder("gpt-3.5-turbo")
        assert encoder3 is not None
    
    @pytest.mark.requires_tiktoken
    def test_count_tokens(self):
        """Test token counting."""
        text = "Hello, world! This is a test."
        count = TokenCounter.count(text, "gpt-4")
        
        # Should return a reasonable count
        assert count > 0
        assert count < 20  # This short text should be less than 20 tokens
    
    @pytest.mark.requires_tiktoken
    def test_truncate(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated. " * 20
        
        truncated = TokenCounter.truncate(text, max_tokens=50, model="gpt-4")
        
        # Truncated text should be shorter
        assert len(truncated) < len(text)
        
        # Token count should be within limit
        count = TokenCounter.count(truncated, "gpt-4")
        assert count <= 50
    
    @pytest.mark.requires_tiktoken
    def test_split_into_chunks(self):
        """Test splitting text into chunks."""
        text = "This is a test sentence. " * 100
        
        chunks = TokenCounter.split_into_chunks(
            text, chunk_size=100, overlap=10, model="gpt-4"
        )
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should be within token limit
        for chunk in chunks:
            count = TokenCounter.count(chunk, "gpt-4")
            assert count <= 100
    
    def test_count_without_tiktoken(self):
        """Test fallback when tiktoken is not available."""
        # This test simulates tiktoken not being available
        # In real use, this would fall back to a simple estimation
        pass  # Skip for now as tiktoken is required


class TestContextOptimizer:
    """Test ContextOptimizer class."""
    
    def test_initialization_with_window(self):
        """Test initialization with predefined window."""
        optimizer = ContextOptimizer(ContextWindow.GPT_4)
        assert optimizer.window == ContextWindow.GPT_4
        assert optimizer.limit == 128_000
        assert optimizer.budget.total == 128_000
    
    def test_initialization_with_custom_limit(self):
        """Test initialization with custom limit."""
        optimizer = ContextOptimizer.with_limit(50_000)
        assert optimizer.window == ContextWindow.CUSTOM
        assert optimizer.limit == 50_000
        assert optimizer.budget.total == 50_000
    
    def test_initialization_with_custom_window_raises(self):
        """Test that CUSTOM window without limit raises error."""
        with pytest.raises(ValueError, match="Use ContextOptimizer.with_limit"):
            ContextOptimizer(ContextWindow.CUSTOM)
    
    @pytest.mark.requires_tiktoken
    def test_can_fit(self):
        """Test checking if content fits."""
        optimizer = ContextOptimizer.with_limit(1000)
        
        short_text = "Hello, world!"
        long_text = "This is a very long text. " * 1000
        
        assert optimizer.can_fit(short_text) is True
        assert optimizer.can_fit(long_text) is False
    
    @pytest.mark.requires_tiktoken
    def test_add_content(self):
        """Test adding content to context."""
        optimizer = ContextOptimizer.with_limit(1000)
        
        text1 = "First piece of content."
        success1, tokens1 = optimizer.add_content(text1, "doc")
        assert success1 is True
        assert tokens1 > 0
        
        # Add more content
        text2 = "Second piece of content."
        success2, tokens2 = optimizer.add_content(text2, "code")
        assert success2 is True
        
        # Try to add content that exceeds limit
        huge_text = "Huge content. " * 1000
        success3, tokens3 = optimizer.add_content(huge_text, "extra")
        assert success3 is False
        assert tokens3 == 0
    
    def test_allocate_budget(self):
        """Test budget allocation."""
        optimizer = ContextOptimizer.with_limit(10_000)
        
        allocations = {
            "documentation": 0.2,
            "source_code": 0.5,
            "tests": 0.2,
            "config": 0.1
        }
        
        result = optimizer.allocate_budget(allocations)
        
        assert result["documentation"] == 2000
        assert result["source_code"] == 5000
        assert result["tests"] == 2000
        assert result["config"] == 1000
    
    def test_allocate_budget_invalid(self):
        """Test invalid budget allocation."""
        optimizer = ContextOptimizer.with_limit(10_000)
        
        # Allocations don't sum to 1.0
        invalid_allocations = {
            "category1": 0.5,
            "category2": 0.3
        }
        
        with pytest.raises(ValueError, match="must sum to 1.0"):
            optimizer.allocate_budget(invalid_allocations)
    
    @pytest.mark.requires_tiktoken
    def test_optimize_content(self):
        """Test content optimization."""
        optimizer = ContextOptimizer.with_limit(1000)
        
        text = "This is a test. " * 100
        
        # Optimize to fit within 100 tokens
        optimized = optimizer.optimize_content(text, target_tokens=100)
        
        # Should be shorter than original
        assert len(optimized) < len(text)
        
        # Should fit within target
        count = TokenCounter.count(optimized, optimizer.model)
        assert count <= 100
    
    def test_get_summary(self):
        """Test summary generation."""
        optimizer = ContextOptimizer(ContextWindow.GPT_4)
        optimizer.budget.allocate("docs", 10_000)
        optimizer.budget.consume(5_000)
        
        summary = optimizer.get_summary()
        
        assert summary["window"] == "GPT_4"
        assert summary["limit"] == 128_000
        assert summary["used"] == 5_000
        assert summary["remaining"] == 113_000  # 128000 - 10000 - 5000
        assert "allocations" in summary