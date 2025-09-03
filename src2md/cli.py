"""
src2md - Source Code to Structured Data

A Python package to convert source code directories into structured data formats
including JSON, JSONL, Markdown, HTML, and plain text. The core generates a 
dictionary representation which can be rendered to any supported format.

Originally designed to provide LLM context, but now supports multiple use cases
including documentation generation, code analysis, and data export.

Usage: src2md path/to/source -o output.md
                            [--format FORMAT]
                            [--doc-pat PATTERN [PATTERN ...]]
                            [--src-pat PATTERN [PATTERN ...]]
                            [--ignore-pat PATTERN [PATTERN ...]]
                            [--ignore-file FILE]
                            [--no-content]
                            [--no-stats]
"""
import argparse
from pathlib import Path
import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from .core import analyze_codebase
from .formatters import to_json, to_jsonl, to_markdown, to_html, to_text
from .utils import default_langs

console = Console()

def main():
    """
    Main function to parse arguments and generate the structured documentation.
    """
    parser = argparse.ArgumentParser(
        description="Convert source code directories to structured data formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  src2md ./myproject -o project.md                 # Generate Markdown
  src2md ./myproject -o project.json --format json # Generate JSON  
  src2md ./myproject -o project.jsonl --format jsonl # Generate JSONL
  src2md ./myproject -o project.html --format html # Generate HTML
  src2md ./myproject --format json --no-content   # JSON without file contents
"""
    )
    
    parser.add_argument(
        "path",
        help="Path to the source directory to analyze."
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file name. If not specified, prints to stdout."
    )
    
    parser.add_argument(
        "--format",
        choices=['json', 'jsonl', 'markdown', 'md', 'html', 'text', 'txt'],
        default='markdown',
        help="Output format (default: markdown). Auto-detected from output file extension if not specified."
    )
    
    parser.add_argument(
        "--doc-pat",
        nargs='+',
        default=['*.md', '*.rst'],
        help="Patterns to identify documentation files (default: ['*.md', '*.rst'])."
    )
    
    parser.add_argument(
        "--src-pat",
        nargs='+',
        default=[f"*{ext}" for ext in default_langs.keys()],
        help="Patterns to identify source files (default: common programming languages)."
    )
    
    parser.add_argument(
        "--ignore-pat",
        nargs='+', 
        default=['.*'],
        help="Patterns to ignore (default: ['.*'] - hidden files)."
    )
    
    parser.add_argument(
        "--ignore-file",
        default=".src2mdignore",
        help="File with patterns to ignore (default: '.src2mdignore')."
    )
    
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Don't include file contents in output (metadata only)."
    )
    
    parser.add_argument(
        "--no-stats",
        action="store_true", 
        help="Don't include statistics in output."
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (ignored for other formats)."
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output."
    )

    args = parser.parse_args()

    # Validate path
    path = Path(args.path)
    if not path.is_dir():
        console.print(f"[red]Error: {args.path} is not a valid directory.[/red]")
        sys.exit(1)

    # Auto-detect format from output file extension
    if args.output and not args.format:
        ext = Path(args.output).suffix.lower()
        format_map = {
            '.json': 'json',
            '.jsonl': 'jsonl', 
            '.md': 'markdown',
            '.html': 'html',
            '.htm': 'html',
            '.txt': 'text'
        }
        args.format = format_map.get(ext, 'markdown')
    
    # Normalize format aliases
    if args.format in ['md']:
        args.format = 'markdown'
    elif args.format in ['txt']:
        args.format = 'text'

    try:
        # Show progress unless quiet
        if not args.quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Analyzing codebase...", total=None)
                
                # Analyze the codebase
                data = analyze_codebase(
                    args.path,
                    doc_pat=args.doc_pat,
                    src_pat=args.src_pat,
                    ignore_pat=args.ignore_pat,
                    include_stats=not args.no_stats,
                    include_content=not args.no_content
                )
                
                progress.update(task, description="Generating output...")
                
                # Generate output
                output = generate_output(data, args.format, args.pretty, not args.no_stats, not args.no_content)
        else:
            # Analyze without progress
            data = analyze_codebase(
                args.path,
                doc_pat=args.doc_pat,
                src_pat=args.src_pat, 
                ignore_pat=args.ignore_pat,
                include_stats=not args.no_stats,
                include_content=not args.no_content
            )
            
            # Generate output
            output = generate_output(data, args.format, args.pretty, not args.no_stats, not args.no_content)
            
    except Exception as e:
        console.print(f"[red]Error analyzing codebase: {e}[/red]")
        if not args.quiet:
            console.print_exception()
        sys.exit(1)

    # Write output
    try:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            
            if not args.quiet:
                # Show summary
                stats = data.get('statistics', {})
                summary_text = Text()
                summary_text.append("✅ Generated ", style="green")
                summary_text.append(f"{args.format.upper()}", style="bold blue")
                summary_text.append(" documentation\n")
                summary_text.append(f"📁 Project: {data['metadata']['project_name']}\n")
                summary_text.append(f"📄 Output: {args.output}\n")
                if stats:
                    summary_text.append(f"📊 {stats.get('total_files', 0)} files analyzed\n")
                    summary_text.append(f"💾 {_format_bytes(stats.get('total_size_bytes', 0))}")
                
                console.print(Panel(summary_text, title="Success", border_style="green"))
        else:
            # Print to stdout
            console.print(output)
            
    except IOError as e:
        console.print(f"[red]Error writing output: {e}[/red]")
        sys.exit(1)


def generate_output(data, format_type, pretty=False, include_stats=True, include_content=True):
    """Generate output in the specified format."""
    if format_type == 'json':
        return to_json(data, pretty=pretty, include_content=include_content)
    elif format_type == 'jsonl':
        return to_jsonl(data, include_content=include_content)
    elif format_type == 'markdown':
        return to_markdown(data, include_stats=include_stats)
    elif format_type == 'html':
        return to_html(data, include_stats=include_stats)
    elif format_type == 'text':
        return to_text(data, include_stats=include_stats)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def _format_bytes(size):
    """Format byte size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    main()
