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
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Convert source code to structured formats with intelligent LLM context optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spinoza/src2md",
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
    ],
    entry_points={
        "console_scripts": [
            "src2md=src2md.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)