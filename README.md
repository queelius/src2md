# src2md

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![PyPI](https://img.shields.io/pypi/v/src2md)
![Python Versions](https://img.shields.io/pypi/pyversions/src2md)

**src2md** is a versatile tool that converts source code directories into comprehensive Markdown documentation. It scans your project structure, includes documentation files like `README.md` or `README.rst`, and embeds source code snippets with proper syntax highlighting. Ideal for providing context to LLMs or sharing project details with collaborators.

## 🚀 **Features**

- **Automatic Documentation Aggregation**: Collects and prioritizes documentation files (e.g., `README.md`, `README.rst`).
- **Syntax-Highlighted Source Code**: Embeds source code files with appropriate language identifiers for Markdown.
- **Flexible File Patterns**: Customize which files to include (whitelist patterns) or exclude (blacklist patterns).
- **Leverages `.src2mdignore`**: Works like `.gitignore`, you can even use that file directly.
- **Simple CLI Interface**: Easy-to-use command-line interface for generating documentation.

## 📦 **Installation**

You can install `src2md` via [PyPI](https://pypi.org/) using `pip`:

```bash
pip install src2md
```

Alternatively, install it directly from the source:

```bash
git clone https://github.com/queelius/src2md.git
cd src2md
pip install .
```

## 🛠️  Usage

Once installed, you can use `src2md` from the command line to generate Markdown documentation for your project.

### Basic Command

```bash
src2md path/to/source -o output.md
```

- `path/to/source`: Path to your project's roo directory.
- `-o output.md`: (Optional) Specifies the output Markdown file name. Defaults to project_documentation.md.

## Advanced Options

- **Specify Documentation Patterns**

  Include additional documentation file types.

  ```bash
  src2md path/to/source -o output.md --doc-pat '*.md' '*.rst' '*.lark'
  ```

- **Specify Source Code Patterns**

  Customize which source files to include. Use '*' to include all files.

  ```bash
  src2md path/to/source -o output.md --src-pat '*.py' '*.js'
  ```

  To include all files as source code:

  ```bash
  src2md path/to/source -o output.md --src-pat '*'
  ```

- **Add Additional Ignore Patterns**

  Exclude specific files or directories.

  ```bash
  src2md path/to/source -o output.md --ignore-pat '*.pyc' 'build/' 'dist/'
  ```

- **Use a Custom Ignore File**

  Specify a custom ignore file. If `.src2mdignore` is present in the source directory, it will be used by default. Here we show how to point to a different file, the `.gitignore` file.

  ```bash
  src2md path/to/source -o output.md --ignore-file .gitignore
  ```

- **Disable .gitignore Usage**

  Do not use .gitignore for ignoring files.

  ```bash
  src2md path/to/source -o output.md --no-use-gitignore
  ```

## Full Example

```bash
src2md proj --doc-pat '*.md' '*.lark' --src-pat '*.py' --ignore-pat '*.pyc' 'build/' 'dist/' '.*'
```

This command generates `project.md` by including all `.md`, and `.lark` documentation files, embedding `.py`, source files, and excluding any `.pyc` files, excluding directories named `build` or `dist`, and ignoring all hidden files and directories (start with `.`).
