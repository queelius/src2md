import os
from pathlib import Path
import pypandoc
import sys
import fnmatch
import pathspec

default_langs = {
    ".py": "python",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".cc": "cpp",
    ".c": "c",
    ".js": "javascript",
    ".java": "java",
    ".ts": "typescript",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".rs": "rust",
    ".lark": "lark",
    ".sh": "bash",
    ".bash": "bash",
    ".bat": "batch",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".rst": "markdown"
}

def convert_rst_to_md(rst_content):
    """
    Convert reStructuredText content to Markdown using pypandoc.

    Args:
        rst_content (str): Content in reStructuredText format.

    Returns:
        str: Converted Markdown content.
    """
    try:
        md_content = pypandoc.convert_text(rst_content, 'md', format='rst')
        return md_content
    except (RuntimeError, OSError) as e:
        print(f"Error converting RST to MD: {e}", file=sys.stderr)
        return rst_content  # Fallback to original content if conversion fails


def load_ignore_patterns(use_gitignore=False, ignore_file=None):
    """
    Load ignore patterns from .gitignore or a custom ignore file.

    Args:
        use_gitignore (bool): Whether to use .gitignore.
        ignore_file (Path or None): Path to a custom ignore file.

    Returns:
        pathspec.PathSpec: Compiled ignore patterns.
    """
    patterns = []
    if use_gitignore:
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_patterns = f.read().splitlines()
                    patterns.extend(gitignore_patterns)
            except (IOError, UnicodeDecodeError) as e:
                print(f"Error reading .gitignore: {e}", file=sys.stderr)

    if ignore_file:
        if ignore_file.exists():
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    custom_patterns = f.read().splitlines()
                    patterns.extend(custom_patterns)
            except (IOError, UnicodeDecodeError) as e:
                print(f"Error reading ignore file {ignore_file}: {e}", file=sys.stderr)
        else:
            print(f"Ignore file {ignore_file} does not exist.", file=sys.stderr)

    # Remove comments and empty lines
    patterns = [p for p in patterns if p and not p.startswith('#')]

    # Add pattern to exclude hidden files and directories
    patterns.append('.*')  # Exclude all hidden files and directories

    # Compile the patterns
    spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    return spec


def find_documentation_files(source_path, doc_patterns, ignore_spec, already_included=None):
    """
    Find documentation files within the source directory based on patterns.

    Args:
        source_path (Path): Path to the source directory.
        doc_patterns (list): List of documentation file patterns.
        ignore_spec (pathspec.PathSpec): Compiled ignore patterns.
        already_included (set): Set of already included documentation files.

    Returns:
        list: List of documentation file paths.
    """
    doc_files = []
    for root, dirs, files in os.walk(source_path):
        # Modify dirs in-place to exclude ignored directories and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and not ignore_spec.match_file(os.path.join(root, d))]

        for file in files:
            if file.startswith('.'):
                continue  # Skip hidden files
            file_path = Path(root) / file
            relative_path = file_path.relative_to(source_path)
            rel_path_str = str(relative_path)
            if ignore_spec.match_file(rel_path_str):
                continue
            for pattern in doc_patterns:
                if fnmatch.fnmatch(file.lower(), pattern.lower()):
                    if already_included and rel_path_str in already_included:
                        continue  # Skip if already included
                    doc_files.append(file_path)
                    if already_included is not None:
                        already_included.add(rel_path_str)
                    break  # Stop checking other patterns once matched
    return doc_files


def include_documentation_files(source_path, markdown_content, doc_patterns, ignore_spec):
    """
    Include documentation files into the markdown content, prioritizing README.*.

    Args:
        source_path (Path): Path to the source directory.
        markdown_content (list): List to append markdown content to.
        doc_patterns (list): List of documentation file patterns.
        ignore_spec (pathspec.PathSpec): Compiled ignore patterns.
    """
    # Prioritize README.* files
    prioritized_patterns = ['README.*']
    other_patterns = [pattern for pattern in doc_patterns if pattern not in prioritized_patterns]

    already_included = set()
    prioritized_docs = find_documentation_files(source_path, prioritized_patterns, ignore_spec, already_included)
    other_docs = find_documentation_files(source_path, other_patterns, ignore_spec, already_included)

    # Combine with prioritized docs first
    doc_files = prioritized_docs + other_docs

    if not doc_files:
        return

    markdown_content.append("## Documentation Files\n")
    markdown_content.append("\n")

    for doc_file in doc_files:
        rel_path = doc_file.relative_to(source_path)
        markdown_content.append(f"### {rel_path}\n")
        markdown_content.append("\n")

        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            print(f"Error reading documentation file {doc_file}: {e}", file=sys.stderr)
            content = f"Error reading file: {e}"

        # Convert to Markdown if .rst
        if doc_file.suffix.lower() == '.rst':
            content = convert_rst_to_md(content)

        markdown_content.append(content)
        markdown_content.append("\n---\n\n")


def get_language_identifier(file_extension):
    """
    Map file extension to language identifier for syntax highlighting in Markdown.

    Args:
        file_extension (str): File extension (e.g., '.py').

    Returns:
        str: Language identifier (e.g., 'python').
    """

    with open("default_langs.json", 'r') as f:
        return f.get(file_extension.lower(), '')


def generate_markdown(source_path, doc_patterns=None, src_patterns=None, ignore_spec=None):
    """
    Generate Markdown content from the source directory.

    Args:
        source_path (Path): Path to the source directory.
        doc_patterns (list): List of documentation file patterns.
        src_patterns (list): List of source file patterns.
        ignore_spec (pathspec.PathSpec): Compiled ignore patterns.

    Returns:
        str: Complete Markdown content.
    """
    markdown_content = []
    source_path = Path(source_path)

    # Add project name as title
    markdown_content.append(f"# Project: {source_path.name}\n\n")

    # Define default documentation patterns
    if doc_patterns is None:
        doc_patterns = ['*.md', '*.rst']

    # Include documentation files like README.md, README.rst, etc.
    include_documentation_files(source_path, markdown_content, doc_patterns, ignore_spec)

    # Collect documentation file paths to exclude them from source files
    doc_files = find_documentation_files(source_path, doc_patterns, ignore_spec)
    doc_file_paths = set(str(p.relative_to(source_path)) for p in doc_files)

    # Traverse the directory
    for root, dirs, files in os.walk(source_path):
        # Modify dirs in-place to exclude ignored directories and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and not ignore_spec.match_file(os.path.join(root, d))]

        # Compute relative path from source_path
        rel_dir = Path(root).relative_to(source_path)
        # Determine heading level based on directory depth
        if rel_dir == Path('.'):
            heading_level = 2  # ## for top-level
        else:
            heading_level = 2 + len(rel_dir.parts)  # Increase heading level based on depth

        # Add directory heading
        if rel_dir != Path('.'):
            markdown_content.append(f"{'#' * heading_level} Directory: `{rel_dir}`\n\n")

        for file in sorted(files):
            if file.startswith('.'):
                continue  # Skip hidden files
            file_path = Path(root) / file
            rel_path = file_path.relative_to(source_path)
            rel_path_str = str(rel_path)

            if rel_path_str in doc_file_paths:
                continue  # Skip documentation files

            # Check if the file matches any source pattern
            if not any(fnmatch.fnmatch(file.lower(), pattern.lower()) for pattern in src_patterns):
                continue

            # Exclude files based on ignore patterns
            if ignore_spec.match_file(rel_path_str):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            except (IOError, UnicodeDecodeError) as e:
                print(f"Error reading source file {file_path}: {e}", file=sys.stderr)
                continue

            # Determine language identifier
            lang = get_language_identifier(file_path.suffix)

            # Add source file section
            markdown_content.append(f"### Source File: `{rel_path}`\n\n")

            # Include source code
            markdown_content.append("#### Source Code\n")
            markdown_content.append("\n```")
            markdown_content.append(f"{lang}\n")
            markdown_content.append(f"{source_code}\n")
            markdown_content.append("```\n\n")

            markdown_content.append("---\n\n")

    return ''.join(markdown_content)
