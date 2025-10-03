"""
RAG Pipeline
Main orchestration logic for Retrieval-Augmented Generation.
"""

from typing import Dict, Any, List
from rag_core.factories.vector_store_factory import get_vector_store
from rag_core.factories.embeddings_factory import get_embeddings
from rag_core.factories.llm_factory import get_llm
from rag_core.config.settings import settings


class RAGPipeline:
    """Main RAG pipeline orchestrating retrieval and generation."""
    
    def __init__(self):
        """Initialize RAG components using factories."""
        self.vector_store = get_vector_store()
        self.embeddings = get_embeddings()
        self.llm = get_llm()
        
        print(f"RAG Pipeline initialized:")
        print(f"  Vector Store: {settings.VECTOR_STORE_TYPE}")
        print(f"  Embeddings: {settings.EMBEDDINGS_TYPE}")
        print(f"  LLM: {settings.LLM_TYPE}")
    
    def query(
        self,
        country: str,
        question: str,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Execute RAG query for a specific country.
        
        Args:
            country: Country namespace to search in
            question: User question
            top_k: Number of chunks to retrieve (defaults to settings)
            
        Returns:
            Dictionary with answer and metadata
        """
        # Validate country
        if country.lower() not in settings.COUNTRIES:
            return {
                'error': f"Invalid country. Supported: {', '.join(settings.COUNTRIES)}",
                'supported_countries': settings.COUNTRIES
            }
        
        country = country.lower()
        top_k = top_k or settings.TOP_K_RESULTS
        
        try:
            # Step 1: Generate query embedding
            query_vector = self.embeddings.embed_query(question)
            
            # Step 2: Retrieve relevant chunks from namespace
            matches = self.vector_store.search(
                query_vector=query_vector,
                namespace=country,
                top_k=top_k
            )
            
            if not matches:
                return {
                    'answer': f"No relevant information found in {country.title()} knowledge base.",
                    'country': country,
                    'sources': []
                }
            
            # Step 3: Extract text chunks and metadata
            context_chunks = [match['metadata']['text'] for match in matches]
            sources = [
                {
                    'file': match['metadata']['source_file'],
                    'score': match['score'],
                    'page': match['metadata'].get('page', 'N/A')
                }
                for match in matches
            ]
            
            # Step 4: Generate answer using LLM with context
            result = self.llm.generate_with_context(
                question=question,
                context_chunks=context_chunks,
                temperature=0.3
            )
            
            # Step 5: Format response
            return {
                'answer': result['answer'],
                'country': country,
                'sources': sources,
                'chunks_used': len(context_chunks),
                'model': result['model']
            }
            
        except Exception as e:
            return {
                'error': f"Error processing query: {str(e)}",
                'country': country
            }
    
    def list_countries(self) -> List[str]:
        """
        Get list of available countries.
        
        Returns:
            List of country names
        """
        return settings.COUNTRIES
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector index.
        
        Returns:
            Index statistics with namespace breakdown
        """
        try:
            stats = self.vector_store.get_stats()
            return {
                'total_vectors': stats['total_vector_count'],
                'namespaces': stats['namespaces'],
                'countries': settings.COUNTRIES
            }
        except Exception as e:
            return {
                'error': f"Error fetching stats: {str(e)}"
            }