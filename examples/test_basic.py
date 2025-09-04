#!/usr/bin/env python3
"""
Basic test to verify the new architecture works.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src2md.core.repository import Repository
from src2md.core.context import ContextWindow, TokenCounter, TokenBudget
from src2md.strategies.importance import ImportanceScorer


def test_basic_functionality():
    """Test basic functionality of the new architecture."""
    print("Testing src2md new architecture...")
    print("=" * 50)
    
    # Test TokenBudget
    print("\n1. Testing TokenBudget...")
    budget = TokenBudget(total=1000)
    assert budget.total == 1000
    assert budget.remaining == 1000
    budget.consume(200)
    assert budget.remaining == 800
    print("   ✅ TokenBudget works")
    
    # Test ContextWindow
    print("\n2. Testing ContextWindow...")
    assert ContextWindow.GPT_4.value == 128_000
    assert ContextWindow.CLAUDE_3.value == 200_000
    print("   ✅ ContextWindow enums work")
    
    # Test ImportanceScorer
    print("\n3. Testing ImportanceScorer...")
    scorer = ImportanceScorer()
    score = scorer._check_entrypoint(Path("main.py"))
    assert score == 1.0
    score = scorer._check_entrypoint(Path("utils.py"))
    assert score == 0.0
    print("   ✅ ImportanceScorer works")
    
    # Test Repository initialization
    print("\n4. Testing Repository...")
    try:
        # Use current directory as test
        repo = Repository(".")
        assert repo.path.exists()
        print("   ✅ Repository initialization works")
        
        # Test fluent API
        result = repo.name("Test").branch("main")
        assert result is repo
        assert repo._name == "Test"
        assert repo._branch == "main"
        print("   ✅ Fluent API works")
        
    except Exception as e:
        print(f"   ❌ Repository test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All basic tests passed!")
    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)