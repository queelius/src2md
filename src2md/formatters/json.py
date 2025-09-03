"""
JSON formatter for repository analysis output.
"""
import json
from typing import Dict, Any

from .base import Formatter


class JSONFormatter(Formatter):
    """Format repository data as JSON."""
    
    def __init__(self, pretty: bool = True, indent: int = 2, **options):
        """
        Initialize JSON formatter.
        
        Args:
            pretty: Pretty-print JSON with indentation
            indent: Number of spaces for indentation
            **options: Additional formatting options
        """
        super().__init__(**options)
        self.pretty = pretty
        self.indent = indent if pretty else None
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as JSON."""
        self.validate_data(data)
        
        # Clean up data if needed
        output_data = self._prepare_data(data)
        
        # Convert to JSON
        return json.dumps(
            output_data,
            indent=self.indent,
            ensure_ascii=False,
            sort_keys=False
        )
    
    def _prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for JSON serialization.
        
        Args:
            data: Raw data dictionary
            
        Returns:
            Cleaned data ready for JSON
        """
        # Create a copy to avoid modifying original
        output = data.copy()
        
        # Ensure all values are JSON-serializable
        # Path objects, datetime objects, etc. should be converted to strings
        
        return output


class JSONLFormatter(Formatter):
    """Format repository data as JSONL (JSON Lines)."""
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format data as JSONL."""
        self.validate_data(data)
        
        lines = []
        
        # Metadata line
        lines.append(json.dumps({
            'type': 'metadata',
            'data': data['metadata']
        }, ensure_ascii=False))
        
        # Statistics line (if present)
        if 'statistics' in data:
            lines.append(json.dumps({
                'type': 'statistics',
                'data': data['statistics']
            }, ensure_ascii=False))
        
        # File lines
        for file_data in data['files']:
            lines.append(json.dumps({
                'type': 'file',
                'data': file_data
            }, ensure_ascii=False))
        
        # Add final newline
        return '\n'.join(lines) + '\n'