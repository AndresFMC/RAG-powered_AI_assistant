"""
Embeddings Factory
Factory for creating embeddings implementations based on configuration.
"""

from rag_core.interfaces.embeddings import EmbeddingsInterface
from rag_core.implementations.embeddings.bedrock_embeddings import BedrockEmbeddings
from rag_core.config.settings import settings


def get_embeddings() -> EmbeddingsInterface:
    """
    Get embeddings implementation based on configuration.
    
    Returns:
        Embeddings instance
        
    Raises:
        ValueError: If embeddings type is not supported
    """
    embeddings_type = settings.EMBEDDINGS_TYPE.lower()
    
    if embeddings_type == 'bedrock':
        return BedrockEmbeddings(
            model_id=settings.BEDROCK_EMBEDDING_MODEL,
            region_name=settings.AWS_REGION
        )
    else:
        raise ValueError(f"Unsupported embeddings type: {embeddings_type}")