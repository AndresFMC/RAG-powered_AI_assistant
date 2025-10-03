"""
LLM Interface
Abstract base class for Large Language Model implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMInterface(ABC):
    """Abstract interface for LLM operations."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """
        Generate text completion from prompt.
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stop_sequences: Optional stop sequences
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def generate_with_context(
        self,
        question: str,
        context_chunks: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate answer using retrieved context chunks.
        
        Args:
            question: User question
            context_chunks: Retrieved text chunks from vector store
            system_prompt: Optional system instructions
            temperature: Sampling temperature
            
        Returns:
            Dictionary with answer and metadata
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model identifier.
        
        Returns:
            Model name/ID
        """
        pass