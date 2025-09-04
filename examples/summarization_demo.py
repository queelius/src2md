#!/usr/bin/env python3
"""
Demonstration of the new summarization and context optimization features.
"""
import sys
from pathlib import Path
# Add the parent directory to path to import src2md as a package
parent = Path(__file__).parent.parent
sys.path.insert(0, str(parent))

from src2md.core.repository import Repository
from src2md.core.context import ContextWindow
from src2md.src2md.strategies.summarization import (
    SummarizationStrategy, 
    SummarizationConfig,
    SummarizationLevel
)


def demo_basic_summarization():
    """Basic summarization example."""
    print("=" * 60)
    print("Basic Summarization Example")
    print("=" * 60)
    
    # Create repository and enable summarization
    repo = (Repository(".")
        .with_summarization(compression_ratio=0.3)
        .with_importance_scoring()
        .analyze())
    
    # Generate markdown with summarization
    output = repo.to_markdown()
    print(f"Generated {len(output)} characters of output")
    print("Files have been intelligently summarized based on importance")


def demo_context_optimization():
    """Context window optimization with progressive summarization."""
    print("\n" + "=" * 60)
    print("Context Window Optimization Example")
    print("=" * 60)
    
    # Optimize for GPT-4's context window
    repo = (Repository(".")
        .optimize_for(ContextWindow.GPT_4)
        .with_importance_scoring()
        .with_summarization(
            compression_ratio=0.2,  # More aggressive compression
            preserve_important=True  # Keep critical files full
        )
        .analyze())
    
    stats = repo.to_dict()['statistics']
    if 'context' in stats:
        print(f"Token usage: {stats['context']['used']}/{stats['context']['limit']}")
        print(f"Utilization: {stats['context']['utilization']:.1%}")


def demo_file_type_summarization():
    """Demonstrate different summarization strategies for file types."""
    print("\n" + "=" * 60)
    print("File Type Specific Summarization")
    print("=" * 60)
    
    # Create summarization strategy with custom config
    config = SummarizationConfig(
        level=SummarizationLevel.DOCSTRINGS,
        preserve_imports=True,
        preserve_exports=True,
        target_compression_ratio=0.25
    )
    
    strategy = SummarizationStrategy(config)
    
    # Sample Python code
    python_code = '''
import os
import sys
from typing import List, Dict

class DataProcessor:
    """Process and analyze data."""
    
    def __init__(self, config: Dict):
        """Initialize with configuration."""
        self.config = config
    
    def process(self, data: List) -> List:
        """Process data items."""
        results = []
        for item in data:
            # Complex processing logic here
            processed = self._transform(item)
            results.append(processed)
        return results
    
    def _transform(self, item):
        """Private transformation method."""
        return item.upper()
'''
    
    summary = strategy.summarize(Path("example.py"), python_code)
    print("Original length:", len(python_code))
    print("Summary length:", len(summary))
    print("Compression ratio:", f"{len(summary)/len(python_code):.1%}")
    print("\nSummary:")
    print(summary)


def demo_llm_summarization():
    """Demonstrate LLM-powered summarization (if configured)."""
    print("\n" + "=" * 60)
    print("LLM-Powered Summarization (Optional)")
    print("=" * 60)
    
    # This will use LLM if API keys are configured
    repo = (Repository(".")
        .with_summarization(
            compression_ratio=0.2,
            use_llm=True,
            llm_model="gpt-3.5-turbo"  # or "claude-3-haiku"
        )
        .optimize_for(ContextWindow.GPT_4)
        .analyze())
    
    print("Note: LLM summarization requires API keys to be configured")
    print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
    print("Without API keys, falls back to rule-based summarization")


def main():
    """Run all demonstrations."""
    print("\n🚀 src2md v2.0 - Summarization & Context Optimization Demo\n")
    
    try:
        demo_basic_summarization()
        demo_context_optimization()
        demo_file_type_summarization()
        demo_llm_summarization()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()