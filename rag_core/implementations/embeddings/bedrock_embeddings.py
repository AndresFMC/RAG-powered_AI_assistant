"""
Bedrock Embeddings Implementation
"""

import os
from typing import List
import boto3
from langchain_aws import BedrockEmbeddings as LangChainBedrockEmbeddings
from rag_core.interfaces.embeddings import EmbeddingsInterface


class BedrockEmbeddings(EmbeddingsInterface):
    """AWS Bedrock implementation of EmbeddingsInterface."""
    
    def __init__(
        self,
        model_id: str = None,
        region_name: str = None
    ):
        """
        Initialize Bedrock embeddings client.
        
        Args:
            model_id: Bedrock model ID (defaults to env var)
            region_name: AWS region (defaults to env var)
        """
        self.model_id = model_id or os.getenv(
            'BEDROCK_EMBEDDING_MODEL',
            'amazon.titan-embed-text-v2:0'
        )
        self.region_name = region_name or os.getenv('AWS_REGION', 'eu-central-1')
        
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=self.region_name
        )
        
        # Use LangChain's Bedrock wrapper
        self.embeddings = LangChainBedrockEmbeddings(
            client=bedrock_client,
            model_id=self.model_id
        )
        
        # Cache dimension
        self._dimension = None
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query text."""
        return self.embeddings.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self.embeddings.embed_documents(texts)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            # Generate a test embedding to get dimension
            test_embedding = self.embed_query("test")
            self._dimension = len(test_embedding)
        
        return self._dimension