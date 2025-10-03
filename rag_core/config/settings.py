"""
Configuration Settings
Centralized configuration for RAG components.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Vector Store Configuration
    VECTOR_STORE_TYPE: str = os.getenv('VECTOR_STORE_TYPE', 'pinecone')
    PINECONE_API_KEY: str = os.getenv('PINECONE_API_KEY', '')
    PINECONE_INDEX_NAME: str = os.getenv('PINECONE_INDEX_NAME', '')
    
    # Embeddings Configuration
    EMBEDDINGS_TYPE: str = os.getenv('EMBEDDINGS_TYPE', 'bedrock')
    BEDROCK_EMBEDDING_MODEL: str = os.getenv(
        'BEDROCK_EMBEDDING_MODEL',
        'amazon.titan-embed-text-v2:0'
    )
    
    # LLM Configuration
    LLM_TYPE: str = os.getenv('LLM_TYPE', 'bedrock')
    BEDROCK_LLM_MODEL: str = os.getenv(
        'BEDROCK_LLM_MODEL',
        'anthropic.claude-3-5-sonnet-20240620-v1:0'
    )
    
    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'eu-central-1')
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '200'))
    TOP_K_RESULTS: int = int(os.getenv('TOP_K_RESULTS', '5'))
    
    # Supported countries
    COUNTRIES: list = ['spain', 'poland', 'colombia', 'italy', 'georgia']


# Global settings instance
settings = Settings()