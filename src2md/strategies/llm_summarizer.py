"""
LLM-powered code summarization for intelligent context optimization.
"""
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Optional LLM imports - these are optional dependencies
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    NONE = "none"  # Fallback when no LLM is available


@dataclass
class LLMConfig:
    """Configuration for LLM-based summarization."""
    provider: LLMProvider = LLMProvider.NONE
    model: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.3
    system_prompt: Optional[str] = None
    
    def __post_init__(self):
        """Auto-detect provider and API key if not specified."""
        if self.provider == LLMProvider.NONE:
            # Try to auto-detect provider
            if HAS_OPENAI and (self.api_key or os.getenv("OPENAI_API_KEY")):
                self.provider = LLMProvider.OPENAI
                self.model = self.model or "gpt-3.5-turbo"
            elif HAS_ANTHROPIC and (self.api_key or os.getenv("ANTHROPIC_API_KEY")):
                self.provider = LLMProvider.ANTHROPIC
                self.model = self.model or "claude-3-haiku-20240307"
        
        # Set API key from environment if not provided
        if not self.api_key:
            if self.provider == LLMProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == LLMProvider.ANTHROPIC:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")


class LLMSummarizer:
    """
    LLM-powered code summarizer for intelligent compression.
    
    This is an optional enhancement that uses LLMs for more intelligent
    summarization when available. Falls back to rule-based summarization
    when LLMs are not configured.
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are a code summarization expert. Your task is to create 
concise, informative summaries of code that preserve the most important information while 
significantly reducing the size. Focus on:

1. Public API signatures and their purpose
2. Core business logic and algorithms
3. Important data structures and their relationships
4. Key dependencies and external interactions
5. Critical error handling and edge cases

Omit:
- Implementation details that can be inferred
- Verbose comments that don't add value
- Repetitive code patterns
- Private helper methods unless critical

Your output should be valid code syntax with strategic use of '...' for omitted sections."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize with optional LLM configuration."""
        self.config = config or LLMConfig()
        self.client = self._init_client()
        
        # Set default system prompt if not provided
        if not self.config.system_prompt:
            self.config.system_prompt = self.DEFAULT_SYSTEM_PROMPT
    
    def _init_client(self):
        """Initialize the appropriate LLM client."""
        if self.config.provider == LLMProvider.OPENAI and HAS_OPENAI:
            return openai.OpenAI(api_key=self.config.api_key)
        elif self.config.provider == LLMProvider.ANTHROPIC and HAS_ANTHROPIC:
            return anthropic.Anthropic(api_key=self.config.api_key)
        return None
    
    def is_available(self) -> bool:
        """Check if LLM summarization is available."""
        return self.client is not None and self.config.api_key is not None
    
    def summarize(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Summarize code using LLM.
        
        Args:
            content: Code content to summarize
            context: Optional context about the file (path, language, importance)
            
        Returns:
            Summarized code or original if LLM unavailable
        """
        if not self.is_available():
            return content  # Return original if LLM not available
        
        # Build context-aware prompt
        prompt = self._build_prompt(content, context)
        
        try:
            if self.config.provider == LLMProvider.OPENAI:
                return self._summarize_openai(prompt)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return self._summarize_anthropic(prompt)
        except Exception as e:
            # Log error and return original content
            print(f"LLM summarization failed: {e}")
            return content
        
        return content
    
    def _build_prompt(self, content: str, context: Optional[Dict[str, Any]]) -> str:
        """Build a context-aware prompt for summarization."""
        parts = []
        
        if context:
            if context.get('file_path'):
                parts.append(f"File: {context['file_path']}")
            if context.get('language'):
                parts.append(f"Language: {context['language']}")
            if context.get('importance_score'):
                parts.append(f"Importance: {context['importance_score']:.2f}")
            if context.get('target_ratio'):
                parts.append(f"Target compression: {int(context['target_ratio'] * 100)}% of original")
        
        if parts:
            context_str = "\n".join(parts)
            prompt = f"Context:\n{context_str}\n\nCode to summarize:\n```\n{content}\n```"
        else:
            prompt = f"Code to summarize:\n```\n{content}\n```"
        
        return prompt
    
    def _summarize_openai(self, prompt: str) -> str:
        """Summarize using OpenAI API."""
        if not HAS_OPENAI or not self.client:
            return prompt
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        return response.choices[0].message.content.strip()
    
    def _summarize_anthropic(self, prompt: str) -> str:
        """Summarize using Anthropic API."""
        if not HAS_ANTHROPIC or not self.client:
            return prompt
        
        response = self.client.messages.create(
            model=self.config.model,
            system=self.config.system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        return response.content[0].text.strip()
    
    def batch_summarize(self, files: List[Dict[str, Any]], 
                        parallel: bool = False) -> List[Dict[str, Any]]:
        """
        Summarize multiple files efficiently.
        
        Args:
            files: List of file dictionaries with 'content' and optional context
            parallel: Whether to process files in parallel (if supported)
            
        Returns:
            List of files with 'summary' field added
        """
        summarized_files = []
        
        for file_data in files:
            if 'content' not in file_data:
                summarized_files.append(file_data)
                continue
            
            context = {
                'file_path': file_data.get('path'),
                'language': file_data.get('language'),
                'importance_score': file_data.get('importance'),
                'target_ratio': file_data.get('target_ratio', 0.3)
            }
            
            summary = self.summarize(file_data['content'], context)
            
            file_data['summary'] = summary
            summarized_files.append(file_data)
        
        return summarized_files
    
    def estimate_cost(self, content: str) -> Dict[str, float]:
        """
        Estimate the cost of summarizing content.
        
        Returns:
            Dict with estimated tokens and cost
        """
        # Rough estimation - actual token count may vary
        input_tokens = len(content) // 4  # Rough estimate
        output_tokens = self.config.max_tokens
        
        # Cost estimates (as of 2024 - these should be updated)
        costs = {
            "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
            "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
            "claude-3-haiku-20240307": {"input": 0.00025 / 1000, "output": 0.00125 / 1000},
            "claude-3-sonnet-20240229": {"input": 0.003 / 1000, "output": 0.015 / 1000},
        }
        
        model_costs = costs.get(self.config.model, {"input": 0.001 / 1000, "output": 0.002 / 1000})
        
        estimated_cost = (
            input_tokens * model_costs["input"] + 
            output_tokens * model_costs["output"]
        )
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "model": self.config.model
        }


class HybridSummarizer:
    """
    Combines rule-based and LLM summarization for optimal results.
    
    Uses rule-based summarization for structured code elements and
    LLM summarization for complex logic and documentation.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """Initialize hybrid summarizer."""
        from .summarization import SummarizationStrategy, SummarizationConfig
        
        self.rule_based = SummarizationStrategy()
        self.llm_summarizer = LLMSummarizer(llm_config) if llm_config else None
    
    def summarize(self, file_path: Path, content: str, 
                  use_llm_for: Optional[List[str]] = None) -> str:
        """
        Summarize using hybrid approach.
        
        Args:
            file_path: Path to the file
            content: File content
            use_llm_for: List of elements to use LLM for (e.g., ['complex_logic', 'docs'])
            
        Returns:
            Summarized content
        """
        # First, use rule-based summarization
        rule_based_summary = self.rule_based.summarize(file_path, content)
        
        # If LLM is available and requested, enhance specific parts
        if self.llm_summarizer and self.llm_summarizer.is_available() and use_llm_for:
            # This is where you could selectively apply LLM to complex parts
            # For now, we'll use LLM for the entire summary if requested
            if 'all' in use_llm_for:
                context = {
                    'file_path': str(file_path),
                    'language': file_path.suffix[1:] if file_path.suffix else None,
                }
                return self.llm_summarizer.summarize(rule_based_summary, context)
        
        return rule_based_summary