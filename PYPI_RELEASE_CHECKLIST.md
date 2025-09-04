# PyPI Release Checklist for src2md v2.1.0

## Pre-Release Verification

### ✅ Package Metadata
- [x] Version updated to 2.1.0 in:
  - [x] setup.py
  - [x] pyproject.toml
  - [x] src2md/__init__.py
- [x] Author information correct (Alex Towell <lex@metafunctor.com>)
- [x] Project URLs updated to https://github.com/queelius/src2md
- [x] License file updated with correct year (2025) and name
- [x] Description clearly communicates value proposition
- [x] Keywords include new features (summarization, ast, code-compression)

### ✅ Dependencies
- [x] Core dependencies specified:
  - rich>=13.0.0
  - tiktoken>=0.5.0
  - pyyaml>=6.0
  - pathspec>=0.11.0
  - astroid>=3.0.0
- [x] Optional dependencies configured:
  - [llm]: openai>=1.0.0, anthropic>=0.8.0
  - [dev]: pytest suite, black, ruff, mypy
- [x] requirements.txt updated
- [x] requirements-llm.txt created for optional LLM deps
- [x] requirements-test.txt maintained

### ✅ Documentation
- [x] CHANGELOG.md updated with v2.1.0 release notes
- [x] RELEASE_NOTES_v2.1.0.md created with comprehensive details
- [x] README.md reflects new features
- [x] API documentation in docs/api/ for new modules
- [x] Usage examples updated in examples/

### ✅ Package Structure
- [x] All modules included in package:
  - src2md/core/
  - src2md/formatters/
  - src2md/strategies/ (including new summarization.py, llm_summarizer.py)
- [x] __init__.py files present in all packages
- [x] MANIFEST.in configured to include all necessary files
- [x] Tests included in src2md/tests/unit/

### ✅ Build Verification
- [x] Package builds successfully: `python -m build`
- [x] Distribution files generated:
  - src2md-2.1.0.tar.gz (source distribution)
  - src2md-2.1.0-py3-none-any.whl (wheel)

## Release Steps

### 1. Final Testing
```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from local wheel
pip install dist/src2md-2.1.0-py3-none-any.whl

# Test basic functionality
src2md --help
python -c "from src2md import Repository, ContextWindow; print('Import successful')"

# Test with optional dependencies
pip install dist/src2md-2.1.0-py3-none-any.whl[llm]
```

### 2. Tag the Release
```bash
git add -A
git commit -m "Release v2.1.0 - Intelligent Summarization & Context Optimization"
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin main --tags
```

### 3. Upload to Test PyPI (Optional)
```bash
# Install/upgrade twine
pip install --upgrade twine

# Upload to test PyPI
twine upload --repository testpypi dist/*

# Test installation from test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ src2md==2.1.0
```

### 4. Upload to PyPI
```bash
# Upload to production PyPI
twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/src2md/2.1.0/
```

### 5. Create GitHub Release
1. Go to https://github.com/queelius/src2md/releases/new
2. Choose tag: v2.1.0
3. Release title: "v2.1.0 - Intelligent Summarization & Context Optimization"
4. Copy content from RELEASE_NOTES_v2.1.0.md
5. Attach distribution files:
   - src2md-2.1.0.tar.gz
   - src2md-2.1.0-py3-none-any.whl
6. Publish release

### 6. Post-Release Verification
```bash
# Install from PyPI
pip install --upgrade src2md==2.1.0

# Verify version
python -c "import src2md; print(src2md.__version__)"

# Test new features
src2md /path/to/project --summarize --compression-ratio 0.5
```

## Announcement Template

### Twitter/X
```
🚀 src2md v2.1.0 is here!

✨ New: Intelligent summarization fits even massive codebases into LLM context windows
🧠 AST-based Python analysis
🌍 Multi-language support
🤖 Optional LLM-powered compression

📦 pip install --upgrade src2md

Docs: github.com/queelius/src2md
```

### Reddit/Discord
```
**src2md v2.1.0 Released - Intelligent Code Summarization for LLMs**

Major new features:
- Smart truncation preserving code structure
- AST-based Python summarization (0.3x-0.8x compression)
- Multi-language strategies (JS/TS, JSON, YAML, tests)
- Optional LLM integration (OpenAI, Anthropic)
- 60% more code fits in GPT-4's context window!

Install: `pip install --upgrade src2md`
GitHub: https://github.com/queelius/src2md
```

## Troubleshooting

### Common Issues
1. **Authentication error**: Ensure PyPI API token is configured
2. **Version conflict**: Check no existing 2.1.0 version on PyPI
3. **Missing files**: Verify MANIFEST.in includes all necessary files
4. **Import errors**: Test in clean virtual environment

### Rollback Plan
If critical issues discovered post-release:
1. Yank release on PyPI (marks as broken, doesn't delete)
2. Fix issues
3. Release as 2.1.1 with hotfix

## Notes
- Package successfully builds with both sdist and wheel
- All new features documented with examples
- Comprehensive test coverage for new functionality
- Backward compatibility maintained with v2.0 API