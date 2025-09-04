#!/usr/bin/env python3
"""
src2md CLI - Simple and powerful command-line interface using the fluent API.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.repository import Repository
from .core.context import ContextWindow

console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert source code to LLM-optimized formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  src2md /path/to/project                     # Basic markdown output
  src2md /path/to/project -o output.md        # Save to file
  src2md /path/to/project --gpt4              # Optimize for GPT-4
  src2md /path/to/project --claude3           # Optimize for Claude 3
  src2md /path/to/project --tokens 50000      # Custom token limit
  src2md /path/to/project --json --pretty     # Pretty JSON output
  src2md /path/to/project --importance        # Enable importance scoring
  src2md /path/to/project --include "src/*.py" --exclude "tests/*"
"""
    )
    
    # Positional arguments
    parser.add_argument(
        "path",
        help="Path to the source directory"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "md", "json", "jsonl", "html", "text"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    
    # Context window optimization
    context_group = parser.add_mutually_exclusive_group()
    context_group.add_argument(
        "--gpt4",
        action="store_true",
        help="Optimize for GPT-4 (128K tokens)"
    )
    context_group.add_argument(
        "--gpt35",
        action="store_true",
        help="Optimize for GPT-3.5 (16K tokens)"
    )
    context_group.add_argument(
        "--claude2",
        action="store_true",
        help="Optimize for Claude 2 (100K tokens)"
    )
    context_group.add_argument(
        "--claude3",
        action="store_true",
        help="Optimize for Claude 3 (200K tokens)"
    )
    context_group.add_argument(
        "--tokens",
        type=int,
        metavar="N",
        help="Custom token limit"
    )
    
    # Analysis options
    parser.add_argument(
        "--importance",
        action="store_true",
        help="Enable file importance scoring"
    )
    
    parser.add_argument(
        "--prioritize",
        nargs="+",
        metavar="PATH",
        help="Prioritize specific paths/files"
    )
    
    parser.add_argument(
        "--summarize-tests",
        action="store_true",
        help="Summarize test files to save tokens"
    )
    
    parser.add_argument(
        "--summarize-docs",
        action="store_true",
        help="Summarize documentation files"
    )
    
    # Summarization options
    summarization_group = parser.add_argument_group("Summarization Options")
    
    summarization_group.add_argument(
        "--summarize",
        action="store_true",
        help="Enable intelligent summarization for files"
    )
    
    summarization_group.add_argument(
        "--compression-ratio",
        type=float,
        default=0.3,
        metavar="RATIO",
        help="Target compression ratio (0.1 = 10%% of original, default: 0.3)"
    )
    
    summarization_group.add_argument(
        "--preserve-important",
        action="store_true",
        default=True,
        help="Keep important files unsummarized (default: True)"
    )
    
    summarization_group.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM for summarization if available"
    )
    
    summarization_group.add_argument(
        "--llm-model",
        help="Specific LLM model to use (e.g., 'gpt-3.5-turbo', 'claude-3-haiku')"
    )
    
    # File filtering
    parser.add_argument(
        "--include",
        nargs="+",
        metavar="PATTERN",
        help="Include patterns (e.g., '*.py' 'src/*')"
    )
    
    parser.add_argument(
        "--exclude",
        nargs="+",
        metavar="PATTERN",
        help="Exclude patterns (e.g., 'tests/*' '*.log')"
    )
    
    # Metadata options
    parser.add_argument(
        "--name",
        help="Project name (default: directory name)"
    )
    
    parser.add_argument(
        "--branch",
        help="Branch name for documentation"
    )
    
    # Control options
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Exclude file contents (metadata only)"
    )
    
    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="Exclude statistics"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Validate path
    path = Path(args.path)
    if not path.exists():
        console.print(f"[red]Error: Path does not exist: {path}[/red]")
        sys.exit(1)
    if not path.is_dir():
        console.print(f"[red]Error: Path is not a directory: {path}[/red]")
        sys.exit(1)
    
    try:
        # Build repository with fluent API
        repo = Repository(path)
        
        # Set metadata
        if args.name:
            repo = repo.name(args.name)
        if args.branch:
            repo = repo.branch(args.branch)
        
        # Apply filters
        if args.include:
            repo = repo.include(*args.include)
        if args.exclude:
            repo = repo.exclude(*args.exclude)
        
        # Apply analysis options
        if args.importance:
            repo = repo.with_importance_scoring()
        
        if args.prioritize:
            repo = repo.prioritize(args.prioritize)
        
        # Apply summarization options
        if args.summarize or args.summarize_tests or args.summarize_docs or args.use_llm:
            repo = repo.with_summarization(
                compression_ratio=args.compression_ratio,
                preserve_important=args.preserve_important,
                use_llm=args.use_llm,
                llm_model=args.llm_model
            )
        
        if args.summarize_tests:
            repo = repo.summarize_tests()
        
        if args.summarize_docs:
            repo = repo.summarize_docs()
        
        # Apply context window optimization
        if args.gpt4:
            repo = repo.optimize_for(ContextWindow.GPT_4)
        elif args.gpt35:
            repo = repo.optimize_for(ContextWindow.GPT_35)
        elif args.claude2:
            repo = repo.optimize_for(ContextWindow.CLAUDE_2)
        elif args.claude3:
            repo = repo.optimize_for(ContextWindow.CLAUDE_3)
        elif args.tokens:
            repo = repo.optimize_for_tokens(args.tokens)
        
        # Configure output options
        repo = repo.with_content(not args.no_content)
        repo = repo.with_stats(not args.no_stats)
        
        # Analyze
        if not args.quiet:
            with console.status("[bold green]Analyzing repository..."):
                repo = repo.analyze()
        else:
            repo = repo.analyze()
        
        # Generate output
        format_type = args.format
        if format_type == "md":
            format_type = "markdown"
        
        if format_type == "markdown":
            output = repo.to_markdown()
        elif format_type == "json":
            output = repo.to_json(pretty=args.pretty)
        elif format_type == "jsonl":
            from .formatters.json import JSONLFormatter
            formatter = JSONLFormatter()
            output = formatter.format(repo.to_dict())
        elif format_type == "html":
            output = repo.to_html()
        elif format_type == "text":
            # Simple text output (markdown without formatting)
            output = repo.to_markdown()
        else:
            raise ValueError(f"Unknown format: {format_type}")
        
        # Write output
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            
            if not args.quiet:
                # Show summary
                summary = Text()
                summary.append("✅ Success!\n", style="bold green")
                summary.append(f"📁 Analyzed: {path.name}\n")
                summary.append(f"📄 Files: {len(repo._files)}\n")
                summary.append(f"💾 Output: {args.output}\n")
                
                if repo._context_optimizer:
                    stats = repo._calculate_statistics()
                    if 'context' in stats:
                        ctx = stats['context']
                        summary.append(f"🎯 Optimized for: {ctx['window']}\n")
                        summary.append(f"📊 Token limit: {ctx['limit']:,}")
                
                console.print(Panel(summary, title="src2md", border_style="green"))
        else:
            # Print to stdout
            print(output)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if not args.quiet:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()