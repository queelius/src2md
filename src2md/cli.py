"""
src2md - Source Code to Markdown

A Python package to map a source code directory into a single Markdown file,
including documentation files (e.g., README.md, README.rst), and source files
whose filenames match specified patterns.

This is primarily used to provide an LLM context about your project, which may
be distributed over multiple file and sub-directories.

Usage: src2md path/to/source -o output.md
                            [--doc-pat PATTERN [PATTERN ...]]
                            [--src-pat PATTERN [PATTERN ...]]
                            [--ignore-pat PATTERN [PATTERN ...]]
                            [--ignore-file FILE]

By default, --ignore-file is set to '.src2mdignore', --doc-pat is set to ['*.md', '*.rst'],
--src-pat is set to all the keys in the `default_langs` dictionary, and --ignore-pat is set to ['.*']
which ignores all hidden files and directories.
"""
import argparse
from pathlib import Path
import sys
from .utils import generate_markdown, default_langs, load_ignore_file

def main():
    """
    Main function to parse arguments and generate the Markdown documentation.
    """

    parser = argparse.ArgumentParser(
        description="Map a source code directory to a Markdown file."
    )
    parser.add_argument(
        "path",
        help="Path to the source directory."
    )
    parser.add_argument(
        "-o", "--out",
        required=True,
        type=str,
        help="Output Markdown file name."
    )
    parser.add_argument(
        "--doc-pat",
        nargs='+',
        default=['*.md', '*.rst'],
        help="Patterns to identify documentation files (e.g., *.md, *.rst). README.* is prioritized. Defaults to ['*.md', '*.rst']."
    )
    parser.add_argument(
        "--src-pat",
        nargs='+',
        default=[f"*{ext}" for ext in default_langs.keys()],
        help="Whitelist patterns to identify files to include (e.g., *.py, *.cpp, *.js). Use '*' to include all files. Defaults to all the keys in `default_langs` dictionary."
    )
    parser.add_argument(
        "--ignore-pat",
        nargs='+',
        default=['.*'],
        help="Blacklist patterns to identify files to ignore (e.g., *.py, *.cpp, *.js). Use '*' to include all files. Defaults to ['.*'], which ignores all hidden files and directories."
    )
    parser.add_argument(
        "--ignore-file",
        default=".src2mdignore",
        help="File with patterns to ignore (e.g., *.py, *.cpp, *.js). Defaults to '.src2mdignore'.")

    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_dir():
        print(f"Error: {args.path} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    ignore_pat = load_ignore_file(path / args.ignore_file)
    if ignore_pat:
        args.ignore_pat.extend(ignore_pat)

    # If '*' is in src_pat, adjust to include all files except those in doc_pat
    if '*' in args.src_pat:
        # Replace '*' with a pattern that matches all files
        args.src_pat = ['*']

    try:
        markdown = generate_markdown(
            args.path,
            doc_pat=args.doc_pat,
            src_pat=args.src_pat,
            ignore_pat=args.ignore_pat)
    except Exception as e:
        print(f"An error occurred while generating documentation: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(markdown)
    except IOError as e:
        print(f"Error writing to output file {args.out}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
