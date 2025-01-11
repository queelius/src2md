# src2md

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![PyPI](https://img.shields.io/pypi/v/src2md)
![Python Versions](https://img.shields.io/pypi/pyversions/src2md)

**src2md** is a versatile tool that converts source code directories into comprehensive Markdown documentation. It scans your project structure, includes documentation files like `README.md` or `README.rst`, and embeds source code snippets with proper syntax highlighting. Ideal for generating project overviews, documentation for large codebases, or providing context to language models.

## 🚀 **Features**

- **Automatic Documentation Aggregation**: Collects and prioritizes documentation files (e.g., `README.md`, `README.rst`).
- **Syntax-Highlighted Source Code**: Embeds source code files with appropriate language identifiers for Markdown.
- **Flexible File Patterns**: Customize which files to include as documentation or source code using patterns.
- **Ignore Hidden Files and Directories**: Automatically excludes hidden files and directories (those starting with `.`).
- **Leverages `.gitignore`**: Respects your `.gitignore` settings to exclude unwanted files.
- **Simple CLI Interface**: Easy-to-use command-line interface for generating documentation.

## 📦 **Installation**

You can install `src2md` via [PyPI](https://pypi.org/) using `pip`:

```bash
pip install src2md
```

Alternatively, install it directly from the source:

```bash
git clone https://github.com/yourusername/src2md.git
cd src2md
pip install .
```

## 🛠️  Usage
Once installed, you can use src2md from the command line to generate Markdown documentation for your project.

### Basic Command

```bash
src2md path/to/source -o output.md
```

- `path/to/source`: Path to your project's root directory.
- `-o output.md`: (Optional) Specifies the output Markdown file name. Defaults to project_documentation.md.

## Advanced Options

- **Specify Documentation Patterns**

  Include additional documentation file types.

  ```bash
  src2md path/to/source -o output.md --doc-patterns '*.md' '*.rst' '*.lark'
  ```

- **Specify Source Code Patterns**

  Customize which source files to include. Use '*' to include all files.

  ```bash
  src2md path/to/source -o output.md --src-patterns '*.py' '*.js'
  ```

  To include all files as source code:

  ```bash
  src2md path/to/source -o output.md --src-patterns '*'
  ```

- **Add Additional Ignore Patterns**

  Exclude specific files or directories.

  ```bash
  src2md path/to/source -o output.md --ignore-patterns '*.pyc' 'build/' 'dist/'
  ```

- **Use a Custom Ignore File**

  Specify a custom ignore file.

  ```bash
  src2md path/to/source -o output.md --ignore-file .src2mdignore
  ```

- **Disable .gitignore Usage**

  Do not use .gitignore for ignoring files.

  ```bash
  src2md path/to/source -o output.md --no-use-gitignore
  ```

## Full Example

```bash
src2md ./my_project -o my_project_docs.md \
    --doc-patterns '*.md' '*.rst' '*.lark' \
    --src-patterns '*.py' '*.cpp' '*.js' \
    --ignore-patterns '*.pyc' 'build/' 'dist/'
```

This command generates my_project_docs.md by including all .md, .rst, and .lark documentation files, embedding .py, .cpp, and .js source files, and excluding any .pyc files and directories named build or dist.
