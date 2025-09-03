#!/usr/bin/env python3
"""
Demo script showing the new src2md fluent API in action.
"""
from pathlib import Path
from src2md import Repository, ContextWindow


def main():
    """Run demo of src2md features."""
    print("=" * 60)
    print("src2md v2.0 - Fluent API Demo")
    print("=" * 60)
    
    # Create a small test directory
    test_dir = Path("demo_project")
    test_dir.mkdir(exist_ok=True)
    
    # Create some sample files
    (test_dir / "main.py").write_text('''#!/usr/bin/env python3
"""Main application module."""

def main():
    """Entry point."""
    print("Hello from src2md demo!")
    return 0

if __name__ == "__main__":
    exit(main())
''')
    
    (test_dir / "utils.py").write_text('''"""Utility functions."""

def process_data(data):
    """Process input data."""
    return {"processed": True, "data": data}

def validate(value):
    """Validate input."""
    return value is not None
''')
    
    (test_dir / "README.md").write_text('''# Demo Project

This is a demo project for src2md.

## Features
- Smart context optimization
- Fluent API
- Multiple output formats
''')
    
    print("\n1. Basic repository analysis:")
    print("-" * 40)
    
    repo = Repository(test_dir)
    repo.analyze()
    
    print(f"✓ Analyzed {len(repo._files)} files")
    for file in repo._files:
        print(f"  - {file.relative_path} ({file.language})")
    
    print("\n2. Fluent API with importance scoring:")
    print("-" * 40)
    
    repo = (Repository(test_dir)
        .name("Demo Project")
        .branch("main")
        .with_importance_scoring()
        .analyze())
    
    print(f"✓ Project: {repo._name} on branch {repo._branch}")
    for file in repo._files:
        if file.importance:
            print(f"  - {file.relative_path}: importance={file.importance.total_score:.2f}")
    
    print("\n3. Context optimization for GPT-4:")
    print("-" * 40)
    
    repo = (Repository(test_dir)
        .optimize_for(ContextWindow.GPT_4)
        .with_importance_scoring()
        .analyze())
    
    stats = repo._calculate_statistics()
    if 'context' in stats:
        ctx = stats['context']
        print(f"✓ Optimized for {ctx['window']} ({ctx['limit']:,} tokens)")
    
    print("\n4. Generate multiple output formats:")
    print("-" * 40)
    
    # Generate Markdown
    markdown = repo.to_markdown()
    print(f"✓ Markdown: {len(markdown)} characters")
    print(f"  Preview: {markdown[:100]}...")
    
    # Generate JSON
    json_output = repo.to_json(pretty=True)
    print(f"✓ JSON: {len(json_output)} characters")
    
    # Generate HTML
    html_output = repo.to_html()
    print(f"✓ HTML: {len(html_output)} characters")
    
    print("\n5. Save outputs:")
    print("-" * 40)
    
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    (output_dir / "output.md").write_text(markdown)
    (output_dir / "output.json").write_text(json_output)
    (output_dir / "output.html").write_text(html_output)
    
    print(f"✓ Saved outputs to {output_dir}/")
    print("  - output.md")
    print("  - output.json")
    print("  - output.html")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    shutil.rmtree(output_dir)
    print("\n(Demo directories cleaned up)")


if __name__ == "__main__":
    main()