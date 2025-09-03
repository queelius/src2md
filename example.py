#!/usr/bin/env python3
"""
Example usage of the new src2md fluent API.
"""
from pathlib import Path
from src2md.core.repository import Repository
from src2md.core.context import ContextWindow


def example_basic():
    """Basic usage example."""
    # Analyze current directory
    repo = Repository(".")
    result = repo.analyze().to_markdown()
    print(result[:500])  # Print first 500 chars


def example_fluent_api():
    """Demonstrate fluent API capabilities."""
    result = (Repository(".")
        .name("MyProject")
        .include("src/", "lib/")
        .exclude("tests/", "docs/")
        .with_importance_scoring()
        .optimize_for(ContextWindow.GPT_4)
        .analyze()
        .to_markdown())
    
    print("Generated optimized markdown for GPT-4 context window")
    return result


def example_context_optimization():
    """Show context window optimization."""
    # Optimize for smaller context window
    result = (Repository(".")
        .optimize_for_tokens(50_000)  # 50K tokens
        .prioritize(["src/core/", "src/api/"])  # Important paths
        .summarize_tests()  # Compress test files
        .analyze()
        .to_json(pretty=True))
    
    print("Generated JSON optimized for 50K tokens")
    return result


def example_multi_format():
    """Export to multiple formats."""
    repo = (Repository(".")
        .name("MyProject")
        .with_importance_scoring()
        .analyze())
    
    # Generate different formats
    markdown = repo.to_markdown()
    json_output = repo.to_json()
    html_output = repo.to_html()
    
    # Save to files
    Path("output.md").write_text(markdown)
    Path("output.json").write_text(json_output)
    Path("output.html").write_text(html_output)
    
    print("Generated output in multiple formats")


if __name__ == "__main__":
    print("src2md Fluent API Examples\n")
    print("=" * 50)
    
    print("\n1. Basic Usage:")
    example_basic()
    
    print("\n2. Fluent API:")
    example_fluent_api()
    
    print("\n3. Context Optimization:")
    example_context_optimization()
    
    print("\n4. Multi-format Export:")
    example_multi_format()