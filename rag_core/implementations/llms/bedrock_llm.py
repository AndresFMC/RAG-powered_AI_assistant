"""
Bedrock LLM Implementation
"""

import os
import json
from typing import List, Dict, Any, Optional
import boto3
from rag_core.interfaces.llm import LLMInterface


class BedrockLLM(LLMInterface):
    """AWS Bedrock implementation of LLMInterface."""
    
    def __init__(
        self,
        model_id: str = None,
        region_name: str = None
    ):
        """
        Initialize Bedrock LLM client.
        
        Args:
            model_id: Bedrock model ID (defaults to env var)
            region_name: AWS region (defaults to env var)
        """
        self.model_id = model_id or os.getenv(
            'BEDROCK_LLM_MODEL',
            'anthropic.claude-3-5-sonnet-20240620-v1:0'
        )
        self.region_name = region_name or os.getenv('AWS_REGION', 'eu-central-1')
        
        # Initialize Bedrock client
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=self.region_name
        )
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate text completion from prompt."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if stop_sequences:
            body["stop_sequences"] = stop_sequences
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def generate_with_context(
        self,
        question: str,
        context_chunks: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Generate answer using retrieved context."""
        # Build context string
        context_str = "\n\n".join([
            f"[Document {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Default system prompt if not provided
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant that answers questions about employment "
                "regulations and hiring policies. Use ONLY the provided context to "
                "answer questions. If the context doesn't contain the answer, say so."
            )
        
        # Build user prompt
        user_prompt = f"""Context information:

{context_str}

Question: {question}

Answer based on the context provided above. If the information is not in the context, clearly state that."""
        
        # Call Bedrock
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        
        return {
            'answer': answer,
            'context_used': len(context_chunks),
            'model': self.model_id
        }
    
    def get_model_name(self) -> str:
        """Get model identifier."""
        return self.model_id