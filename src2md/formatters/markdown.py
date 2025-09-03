"""
Markdown formatter for repository analysis output.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import StreamingFormatter


class MarkdownFormatter(StreamingFormatter):
    """Format repository data as Markdown."""
    
    def __init__(self, include_toc: bool = True, include_stats: bool = True, **options):
        """
        Initialize Markdown formatter.
        
        Args:
            include_toc: Include table of contents
            include_stats: Include statistics section
            **options: Additional formatting options
        """
        super().__init__(**options)
        self.include_toc = include_toc
        self.include_stats = include_stats
    
    def format_header(self, metadata: Dict[str, Any]) -> str:
        """Format the header with title and metadata."""
        lines = []
        
        # Title
        name = metadata.get('name', 'Repository')
        lines.append(f"# {name}\n")
        
        # Metadata
        if 'path' in metadata:
            lines.append(f"**Path:** `{metadata['path']}`\n")
        if 'branch' in metadata and metadata['branch']:
            lines.append(f"**Branch:** `{metadata['branch']}`\n")
        
        timestamp = datetime.now().isoformat()
        lines.append(f"*Generated on {timestamp}*\n")
        
        # Table of Contents
        if self.include_toc:
            lines.append("\n## Table of Contents\n")
            lines.append("- [Overview](#overview)\n")
            if self.include_stats:
                lines.append("- [Statistics](#statistics)\n")
            lines.append("- [Files](#files)\n")
        
        lines.append("\n## Overview\n")
        lines.append(f"This repository contains {metadata.get('file_count', 0)} analyzed files.\n")
        
        return ''.join(lines)
    
    def format_file(self, file_data: Dict[str, Any]) -> str:
        """Format a single file entry."""
        lines = []
        
        path = file_data.get('path', 'unknown')
        language = file_data.get('language', '')
        
        # File header
        lines.append(f"\n### `{path}`\n")
        
        # Metadata
        metadata_parts = []
        if language:
            metadata_parts.append(f"Language: {language}")
        if 'size' in file_data:
            size = self._format_size(file_data['size'])
            metadata_parts.append(f"Size: {size}")
        if 'importance' in file_data:
            score = file_data['importance']
            metadata_parts.append(f"Importance: {score:.2f}")
        
        if metadata_parts:
            lines.append(f"*{' | '.join(metadata_parts)}*\n")
        
        # Content or summary
        if 'content' in file_data:
            lines.append(f"\n```{language}\n")
            lines.append(file_data['content'])
            if not file_data['content'].endswith('\n'):
                lines.append('\n')
            lines.append("```\n")
        elif 'summary' in file_data:
            lines.append(f"\n{file_data['summary']}\n")
        
        return ''.join(lines)
    
    def format_footer(self, statistics: Optional[Dict[str, Any]] = None) -> str:
        """Format the footer with statistics."""
        if not self.include_stats or not statistics:
            return ""
        
        lines = ["\n## Statistics\n"]
        
        # General stats
        if 'total_files' in statistics:
            lines.append(f"- **Total Files:** {statistics['total_files']}\n")
        if 'total_size' in statistics:
            size = self._format_size(statistics['total_size'])
            lines.append(f"- **Total Size:** {size}\n")
        
        # Language breakdown
        if 'languages' in statistics and statistics['languages']:
            lines.append("\n### Language Breakdown\n")
            lines.append("| Language | Files | Size |\n")
            lines.append("|----------|-------|------|\n")
            
            for lang, data in sorted(statistics['languages'].items()):
                count = data.get('count', 0)
                size = self._format_size(data.get('size', 0))
                lines.append(f"| {lang} | {count} | {size} |\n")
        
        # Context window usage
        if 'context' in statistics:
            context = statistics['context']
            lines.append("\n### Context Window Usage\n")
            lines.append(f"- **Window Type:** {context.get('window', 'Unknown')}\n")
            lines.append(f"- **Token Limit:** {context.get('limit', 0):,}\n")
            lines.append(f"- **Tokens Used:** {context.get('used', 0):,}\n")
            lines.append(f"- **Utilization:** {context.get('utilization', 0):.1%}\n")
        
        return ''.join(lines)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def format_tree(self, files: List[Dict[str, Any]]) -> str:
        """
        Format files as a tree structure.
        
        Args:
            files: List of file data dictionaries
            
        Returns:
            Tree representation as string
        """
        lines = ["\n## File Tree\n", "```\n"]
        
        # Build tree structure
        tree = {}
        for file_data in files:
            path = file_data.get('path', '')
            parts = path.split('/')
            
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file
            current[parts[-1]] = None
        
        # Render tree
        def render_tree(node: Dict, prefix: str = "", is_last: bool = True):
            items = list(node.items())
            for i, (name, children) in enumerate(items):
                is_last_item = i == len(items) - 1
                
                # Print current item
                connector = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{connector}{name}\n")
                
                # Recurse for directories
                if children is not None:
                    extension = "    " if is_last_item else "│   "
                    render_tree(children, prefix + extension, is_last_item)
        
        render_tree(tree)
        lines.append("```\n")
        
        return ''.join(lines)