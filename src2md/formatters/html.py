"""
HTML formatter for repository analysis output.
"""
from typing import Dict, Any, Optional
import html
from datetime import datetime

from .base import StreamingFormatter


class HTMLFormatter(StreamingFormatter):
    """Format repository data as HTML."""
    
    def __init__(self, include_styles: bool = True, **options):
        """
        Initialize HTML formatter.
        
        Args:
            include_styles: Include CSS styles in output
            **options: Additional formatting options
        """
        super().__init__(**options)
        self.include_styles = include_styles
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as complete HTML document."""
        self.validate_data(data)
        
        name = data['metadata'].get('name', 'Repository')
        
        parts = [
            '<!DOCTYPE html>\n',
            '<html lang="en">\n',
            '<head>\n',
            '    <meta charset="UTF-8">\n',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n',
            f'    <title>{html.escape(name)}</title>\n',
        ]
        
        if self.include_styles:
            parts.append(self._get_styles())
        
        parts.extend([
            '</head>\n',
            '<body>\n',
            '    <div class="container">\n',
        ])
        
        # Add content
        parts.append(self.format_header(data['metadata']))
        
        # Add files
        parts.append('        <section id="files">\n')
        parts.append('            <h2>Files</h2>\n')
        for file_data in data['files']:
            parts.append(self.format_file(file_data))
        parts.append('        </section>\n')
        
        # Add footer
        if 'statistics' in data:
            parts.append(self.format_footer(data['statistics']))
        
        parts.extend([
            '    </div>\n',
            '</body>\n',
            '</html>\n'
        ])
        
        return ''.join(parts)
    
    def format_header(self, metadata: Dict[str, Any]) -> str:
        """Format the header with title and metadata."""
        name = html.escape(metadata.get('name', 'Repository'))
        
        parts = [
            '        <header>\n',
            f'            <h1>{name}</h1>\n',
            '            <div class="metadata">\n'
        ]
        
        if 'path' in metadata:
            path = html.escape(metadata['path'])
            parts.append(f'                <p><strong>Path:</strong> <code>{path}</code></p>\n')
        
        if 'branch' in metadata and metadata['branch']:
            branch = html.escape(metadata['branch'])
            parts.append(f'                <p><strong>Branch:</strong> <code>{branch}</code></p>\n')
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        parts.append(f'                <p><em>Generated on {timestamp}</em></p>\n')
        
        parts.extend([
            '            </div>\n',
            '        </header>\n'
        ])
        
        return ''.join(parts)
    
    def format_file(self, file_data: Dict[str, Any]) -> str:
        """Format a single file entry."""
        path = html.escape(file_data.get('path', 'unknown'))
        language = file_data.get('language', '')
        
        parts = [
            '            <article class="file">\n',
            f'                <h3><code>{path}</code></h3>\n'
        ]
        
        # Metadata
        metadata_items = []
        if language:
            metadata_items.append(f'Language: {html.escape(language)}')
        if 'size' in file_data:
            size = self._format_size(file_data['size'])
            metadata_items.append(f'Size: {size}')
        if 'importance' in file_data:
            score = file_data['importance']
            metadata_items.append(f'Importance: {score:.2f}')
        
        if metadata_items:
            parts.append('                <div class="file-meta">\n')
            for item in metadata_items:
                parts.append(f'                    <span>{item}</span>\n')
            parts.append('                </div>\n')
        
        # Content or summary
        if 'content' in file_data:
            content = html.escape(file_data['content'])
            parts.append(f'                <pre><code class="language-{language}">{content}</code></pre>\n')
        elif 'summary' in file_data:
            summary = html.escape(file_data['summary'])
            parts.append(f'                <div class="summary">{summary}</div>\n')
        
        parts.append('            </article>\n')
        
        return ''.join(parts)
    
    def format_footer(self, statistics: Optional[Dict[str, Any]] = None) -> str:
        """Format the footer with statistics."""
        if not statistics:
            return ""
        
        parts = [
            '        <section id="statistics">\n',
            '            <h2>Statistics</h2>\n'
        ]
        
        # General stats
        parts.append('            <div class="stats-general">\n')
        if 'total_files' in statistics:
            parts.append(f'                <p><strong>Total Files:</strong> {statistics["total_files"]}</p>\n')
        if 'total_size' in statistics:
            size = self._format_size(statistics['total_size'])
            parts.append(f'                <p><strong>Total Size:</strong> {size}</p>\n')
        parts.append('            </div>\n')
        
        # Language breakdown
        if 'languages' in statistics and statistics['languages']:
            parts.append('            <div class="stats-languages">\n')
            parts.append('                <h3>Language Breakdown</h3>\n')
            parts.append('                <table>\n')
            parts.append('                    <thead>\n')
            parts.append('                        <tr><th>Language</th><th>Files</th><th>Size</th></tr>\n')
            parts.append('                    </thead>\n')
            parts.append('                    <tbody>\n')
            
            for lang, data in sorted(statistics['languages'].items()):
                count = data.get('count', 0)
                size = self._format_size(data.get('size', 0))
                parts.append(f'                        <tr><td>{html.escape(lang)}</td><td>{count}</td><td>{size}</td></tr>\n')
            
            parts.append('                    </tbody>\n')
            parts.append('                </table>\n')
            parts.append('            </div>\n')
        
        parts.append('        </section>\n')
        
        return ''.join(parts)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _get_styles(self) -> str:
        """Get CSS styles for the HTML document."""
        return '''    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        header {
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #34495e;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        h3 {
            color: #555;
            margin: 20px 0 10px;
        }
        
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }
        
        pre {
            background: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        pre code {
            background: none;
            padding: 0;
        }
        
        .metadata {
            color: #666;
            font-size: 0.95em;
        }
        
        .file {
            margin-bottom: 30px;
            padding: 15px;
            background: #fafafa;
            border-left: 3px solid #3498db;
            border-radius: 3px;
        }
        
        .file-meta {
            color: #777;
            font-size: 0.9em;
            margin: 5px 0;
        }
        
        .file-meta span {
            margin-right: 15px;
        }
        
        .summary {
            padding: 10px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 3px;
            margin: 10px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            text-align: left;
            padding: 10px;
            border: 1px solid #ddd;
        }
        
        th {
            background: #f4f4f4;
            font-weight: bold;
        }
        
        tbody tr:hover {
            background: #f9f9f9;
        }
        
        .stats-general p {
            margin: 5px 0;
        }
        
        .stats-languages {
            margin-top: 20px;
        }
    </style>
'''