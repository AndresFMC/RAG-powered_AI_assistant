"""
LLM Factory
Factory for creating LLM implementations based on configuration.
"""

from rag_core.interfaces.llm import LLMInterface
from rag_core.implementations.llms.bedrock_llm import BedrockLLM
from rag_core.config.settings import settings


def get_llm() -> LLMInterface:
    """
    Get LLM implementation based on configuration.
    
    Returns:
        LLM instance
        
    Raises:
        ValueError: If LLM type is not supported
    """
    llm_type = settings.LLM_TYPE.lower()
    
    if llm_type == 'bedrock':
        return BedrockLLM(
            model_id=settings.BEDROCK_LLM_MODEL,
            region_name=settings.AWS_REGION
        )
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")