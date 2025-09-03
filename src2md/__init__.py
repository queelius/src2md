"""
src2md - Source Code to Structured Data

A versatile tool that converts source code directories into structured data formats
with intelligent context window optimization for LLMs.

Main classes:
- Repository: Core class with fluent API for analyzing repositories
- ContextWindow: Predefined context windows for common LLMs
- ImportanceScorer: Score files by importance for optimization
"""

from .core.repository import Repository
from .core.context import ContextWindow, ContextOptimizer, TokenCounter
from .strategies.importance import ImportanceScorer, ImportanceWeights

__version__ = '2.0.0'
__all__ = [
    'Repository',
    'ContextWindow',
    'ContextOptimizer',
    'TokenCounter',
    'ImportanceScorer',
    'ImportanceWeights',
]