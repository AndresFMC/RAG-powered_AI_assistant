"""
Quick local test of RAG pipeline
Run this to verify everything works before Lambda deployment
"""

from rag_core.core.rag_pipeline import RAGPipeline

def main():
    print("Testing RAG Pipeline locally...")
    print("="*60)
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    print("\n1. Testing list_countries():")
    countries = pipeline.list_countries()
    print(f"   Available countries: {countries}")
    
    print("\n2. Testing get_index_stats():")
    stats = pipeline.get_index_stats()
    print(f"   Total vectors: {stats.get('total_vectors', 0)}")
    print(f"   Namespaces: {list(stats.get('namespaces', {}).keys())}")
    
    print("\n3. Testing query():")
    result = pipeline.query(
        country="spain",
        question="What is the probation period in Spain?"
    )
    
    if 'error' in result:
        print(f"   ✗ Error: {result['error']}")
    else:
        print(f"   ✓ Answer: {result['answer'][:200]}...")
        print(f"   Sources: {len(result['sources'])} documents")
        print(f"   Model: {result['model']}")
    
    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    main()