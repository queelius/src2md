"""
src2md - Source Code to Markdown

A script to map a source code directory into a single Markdown file,
including documentation files (e.g., README.md, README.rst),
and source code of various file types. This is primarily used to provide an LLM
context about your project, which may be distributed over multiple files
and sub-directories.

Usage:
    ./src2md path/to/source -o output.md [--doc-patterns PATTERN [PATTERN ...]]
                                [--src-patterns PATTERN [PATTERN ...]]
                                [--ignore-patterns PATTERN [PATTERN ...]]
                                [--ignore-file PATH]
"""
import argparse
import json
from pathlib import Path
import pathspec
import sys
from .utils import generate_markdown, load_ignore_patterns, default_langs

def main():
    """
    Main function to parse arguments and generate the Markdown documentation.
    """

    parser = argparse.ArgumentParser(
        description="Map a source code directory to a Markdown file."
    )
    parser.add_argument(
        "source_dir",
        help="Path to the source code directory."
    )
    parser.add_argument(
        "-o", "--output",
        default="project_documentation.md",
        help="Output Markdown file name. Defaults to 'project_documentation.md'."
    )
    parser.add_argument(
        "--doc-patterns",
        nargs='+',
        default=['*.md', '*.rst'],
        help="Patterns to identify documentation files (e.g., *.md, *.rst). README.* is prioritized. Defaults to ['*.md', '*.rst']."
    )
    parser.add_argument(
        "--src-patterns",
        nargs='+',
        default=list(default_langs.keys()),
        help="Patterns to identify source code files (e.g., *.py, *.cpp, *.js). Use '*' to include all files. Defaults to all the keys in default_langs dictionary."
    )
    parser.add_argument(
        "--ignore-patterns",
        nargs='*',
        default=[],
        help="Additional ignore patterns (e.g., '*.pyc', 'build/', 'dist/'). Defaults to []."
    )
    parser.add_argument(
        "--ignore-file",
        type=str,
        default=None,
        help="Path to a custom ignore file (e.g., .src2mdignore). Defaults to None."
    )
    parser.add_argument(
        "--use-gitignore",
        action="store_true",
        default=True,
        help="Use .gitignore to determine which files/directories to exclude. (Default: True)"
    )

    args = parser.parse_args()

    source_path = Path(args.source_dir)
    if not source_path.is_dir():
        print(f"Error: {args.source_dir} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Load ignore patterns
    ignore_spec = load_ignore_patterns(
        use_gitignore=args.use_gitignore,
        ignore_file=Path(args.ignore_file) if args.ignore_file else None
    )

    # Add additional ignore patterns from command-line arguments
    if args.ignore_patterns:
        # Convert patterns to a PathSpec object
        additional_ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', args.ignore_patterns)
        # Combine with existing ignore_spec
        combined_patterns = list(ignore_spec.patterns) + list(additional_ignore_spec.patterns)
        ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', combined_patterns)

    # If '*' is in src_patterns, adjust to include all files except those excluded by ignore_spec and doc_patterns
    if '*' in args.src_patterns:
        # Replace '*' with a pattern that matches all files
        args.src_patterns = ['*']

    try:
        markdown = generate_markdown(
            source_path,
            doc_patterns=args.doc_patterns,
            src_patterns=args.src_patterns,
            ignore_spec=ignore_spec
        )
    except Exception as e:
        print(f"An error occurred while generating documentation: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Documentation generated and saved to '{args.output}'")
    except IOError as e:
        print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
