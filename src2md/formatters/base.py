"""
Base formatter interface for output generation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Formatter(ABC):
    """Abstract base class for all formatters."""
    
    def __init__(self, **options):
        """
        Initialize formatter with options.
        
        Args:
            **options: Formatter-specific options
        """
        self.options = options
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format repository data into output string.
        
        Args:
            data: Repository analysis data
            
        Returns:
            Formatted string output
        """
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data structure.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, raises ValueError if not
        """
        required_keys = ['metadata', 'files']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        if not isinstance(data['files'], list):
            raise ValueError("'files' must be a list")
        
        return True
    
    def get_option(self, key: str, default: Any = None) -> Any:
        """
        Get formatter option with default.
        
        Args:
            key: Option key
            default: Default value if not set
            
        Returns:
            Option value or default
        """
        return self.options.get(key, default)


class StreamingFormatter(Formatter):
    """Base class for formatters that support streaming output."""
    
    @abstractmethod
    def format_header(self, metadata: Dict[str, Any]) -> str:
        """Format the header/metadata section."""
        pass
    
    @abstractmethod
    def format_file(self, file_data: Dict[str, Any]) -> str:
        """Format a single file entry."""
        pass
    
    @abstractmethod
    def format_footer(self, statistics: Optional[Dict[str, Any]] = None) -> str:
        """Format the footer/summary section."""
        pass
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data using streaming approach.
        
        This can be overridden for batch processing.
        """
        self.validate_data(data)
        
        parts = []
        
        # Header
        parts.append(self.format_header(data['metadata']))
        
        # Files
        for file_data in data['files']:
            parts.append(self.format_file(file_data))
        
        # Footer
        statistics = data.get('statistics')
        parts.append(self.format_footer(statistics))
        
        return ''.join(parts)