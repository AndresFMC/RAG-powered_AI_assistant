"""
Vector Store Factory
Factory for creating vector store implementations based on configuration.
"""

from rag_core.interfaces.vector_store import VectorStoreInterface
from rag_core.implementations.vector_stores.pinecone_store import PineconeStore
from rag_core.config.settings import settings


def get_vector_store() -> VectorStoreInterface:
    """
    Get vector store implementation based on configuration.
    
    Returns:
        Vector store instance
        
    Raises:
        ValueError: If vector store type is not supported
    """
    store_type = settings.VECTOR_STORE_TYPE.lower()
    
    if store_type == 'pinecone':
        return PineconeStore(
            api_key=settings.PINECONE_API_KEY,
            index_name=settings.PINECONE_INDEX_NAME
        )
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")