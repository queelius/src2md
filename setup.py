"""
Setup script for src2md package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="src2md",
    version="2.1.0",
    author="Alex Towell",
    author_email="lex@metafunctor.com",
    description="Convert source code to structured, context-optimized markdown for LLMs with intelligent summarization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/queelius/src2md",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "tiktoken>=0.5.0",
        "pyyaml>=6.0",
        "pathspec>=0.11.0",
        "astroid>=3.0.0",  # For AST-based Python analysis
    ],
    extras_require={
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.8.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "pytest-timeout>=2.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "src2md=src2md.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)