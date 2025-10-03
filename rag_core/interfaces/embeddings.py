"""
Embeddings Interface
Abstract base class for embedding model implementations.
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingsInterface(ABC):
    """Abstract interface for text embedding operations."""
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of document texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors.
        
        Returns:
            Dimension size (e.g., 1024 for Titan v2)
        """
        pass