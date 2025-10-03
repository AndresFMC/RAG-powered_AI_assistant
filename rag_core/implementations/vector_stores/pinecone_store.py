"""
Pinecone Vector Store Implementation
"""

import os
from typing import List, Dict, Any
from pinecone import Pinecone
from rag_core.interfaces.vector_store import VectorStoreInterface


class PineconeStore(VectorStoreInterface):
    """Pinecone implementation of VectorStoreInterface."""
    
    def __init__(self, api_key: str = None, index_name: str = None):
        """
        Initialize Pinecone client and index.
        
        Args:
            api_key: Pinecone API key (defaults to env var)
            index_name: Index name (defaults to env var)
        """
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME')
        
        if not self.api_key:
            raise ValueError("Pinecone API key not provided")
        if not self.index_name:
            raise ValueError("Pinecone index name not provided")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)
    
    def search(
        self,
        query_vector: List[float],
        namespace: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in namespace."""
        query_params = {
            'vector': query_vector,
            'top_k': top_k,
            'namespace': namespace,
            'include_metadata': True
        }
        
        if filter_metadata:
            query_params['filter'] = filter_metadata
        
        results = self.index.query(**query_params)
        
        # Format results
        matches = []
        for match in results.matches:
            matches.append({
                'id': match.id,
                'score': match.score,
                'metadata': match.metadata
            })
        
        return matches
    
    def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str
    ) -> Dict[str, Any]:
        """Insert or update vectors in namespace."""
        result = self.index.upsert(
            vectors=vectors,
            namespace=namespace
        )
        
        return {
            'upserted_count': result.upserted_count,
            'namespace': namespace
        }
    
    def delete_namespace(self, namespace: str) -> bool:
        """Delete all vectors in namespace."""
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            return True
        except Exception as e:
            print(f"Error deleting namespace {namespace}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        stats = self.index.describe_index_stats()
        
        return {
            'total_vector_count': stats.total_vector_count,
            'namespaces': {
                ns: {'vector_count': ns_stats.vector_count}
                for ns, ns_stats in stats.namespaces.items()
            }
        }