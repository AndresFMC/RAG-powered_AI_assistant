"""
Vector Store Interface
Abstract base class for vector store implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class VectorStoreInterface(ABC):
    """Abstract interface for vector store operations."""
    
    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        namespace: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the specified namespace.
        
        Args:
            query_vector: Embedding vector to search with
            namespace: Namespace to search in (country isolation)
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matches with metadata and scores
        """
        pass
    
    @abstractmethod
    def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str
    ) -> Dict[str, Any]:
        """
        Insert or update vectors in the specified namespace.
        
        Args:
            vectors: List of vector objects with id, values, metadata
            namespace: Namespace to upsert into
            
        Returns:
            Upsert operation result
        """
        pass
    
    @abstractmethod
    def delete_namespace(self, namespace: str) -> bool:
        """
        Delete all vectors in a namespace.
        
        Args:
            namespace: Namespace to delete
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics including namespace breakdown.
        
        Returns:
            Statistics dictionary
        """
        pass