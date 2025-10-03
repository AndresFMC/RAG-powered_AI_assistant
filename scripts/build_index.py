"""
Build Index Script - RAG Powered AI Assistant
Indexes PDF documents into Pinecone with namespace isolation per country.
Updated to use modular rag_core architecture.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import rag_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_core.factories.vector_store_factory import get_vector_store
from rag_core.factories.embeddings_factory import get_embeddings
from rag_core.config.settings import settings

# Load environment variables
load_dotenv()

# LangSmith configuration
if os.getenv('LANGSMITH_TRACING') == 'true':
    print(f"✓ LangSmith tracing enabled")
    print(f"  Endpoint: {os.getenv('LANGSMITH_ENDPOINT')}")
    print(f"  Project: {os.getenv('LANGSMITH_PROJECT')}")

# Configuration
COUNTRIES = settings.COUNTRIES
DATA_DIR = Path(__file__).parent.parent / 'data'
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP


class IndexBuilder:
    def __init__(self):
        """Initialize components using factories."""
        print("Initializing IndexBuilder...")
        
        # Use factories to get implementations
        self.vector_store = get_vector_store()
        self.embeddings = get_embeddings()
        
        # Verify embedding dimensions
        embedding_dim = self.embeddings.get_dimension()
        print(f"Embedding dimensions: {embedding_dim}")
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✓ IndexBuilder initialized")
    
    def load_and_split_pdf(self, pdf_path: Path) -> list:
        """Load PDF and split into chunks."""
        print(f"  Loading: {pdf_path.name}")
        
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()
        
        # Split documents
        chunks = self.text_splitter.split_documents(documents)
        
        print(f"  → Generated {len(chunks)} chunks")
        return chunks
    
    def process_country(self, country: str):
        """Process all PDFs for a specific country."""
        print(f"\n{'='*60}")
        print(f"Processing: {country.upper()}")
        print(f"{'='*60}")
        
        country_dir = DATA_DIR / country
        if not country_dir.exists():
            print(f"✗ Directory not found: {country_dir}")
            return
        
        # Get all PDFs
        pdf_files = sorted(country_dir.glob('*.pdf'))
        if not pdf_files:
            print(f"✗ No PDF files found in {country_dir}")
            return
        
        print(f"Found {len(pdf_files)} PDF files")
        
        all_chunks = []
        
        # Process each PDF
        for pdf_path in pdf_files:
            chunks = self.load_and_split_pdf(pdf_path)
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata.update({
                    'country': country,
                    'source_file': pdf_path.name,
                    'namespace': country
                })
            
            all_chunks.extend(chunks)
        
        print(f"\nTotal chunks for {country}: {len(all_chunks)}")
        
        # Generate embeddings and upsert
        self.upsert_chunks(all_chunks, country)
    
    def upsert_chunks(self, chunks: list, namespace: str):
        """Generate embeddings and upsert to vector store."""
        print(f"Generating embeddings and upserting to namespace '{namespace}'...")
        
        batch_size = 100
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            # Prepare vectors
            vectors = []
            for idx, chunk in enumerate(batch):
                # Generate embedding using factory-provided embeddings
                embedding = self.embeddings.embed_query(chunk.page_content)
                
                # Create vector ID
                vector_id = f"{namespace}_{i+idx}"
                
                # Prepare metadata
                metadata = {
                    'text': chunk.page_content,
                    'country': chunk.metadata['country'],
                    'source_file': chunk.metadata['source_file'],
                    'page': chunk.metadata.get('page', 0)
                }
                
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Upsert using factory-provided vector store
            self.vector_store.upsert(
                vectors=vectors,
                namespace=namespace
            )
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        print(f"✓ Successfully indexed {len(chunks)} chunks to namespace '{namespace}'")
    
    def verify_indexing(self):
        """Verify that all namespaces have been populated."""
        print(f"\n{'='*60}")
        print("VERIFICATION")
        print(f"{'='*60}")
        
        # Wait for eventual consistency
        print("\nWaiting 30s for vector store eventual consistency...")
        time.sleep(30)
        
        stats = self.vector_store.get_stats()
        
        print(f"\nTotal vectors: {stats['total_vector_count']}")
        print(f"\nNamespace breakdown:")
        
        for namespace, ns_stats in stats['namespaces'].items():
            print(f"  • {namespace}: {ns_stats['vector_count']} vectors")
        
        # Check if all countries are present
        existing_namespaces = set(stats['namespaces'].keys())
        missing = set(COUNTRIES) - existing_namespaces
        
        if missing:
            print(f"\n⚠ Missing namespaces: {missing}")
        else:
            print(f"\n✓ All {len(COUNTRIES)} countries indexed successfully!")
    
    def run(self):
        """Main execution method."""
        print("\n" + "="*60)
        print("RAG POWERED AI ASSISTANT - INDEX BUILDER")
        print("="*60)
        
        start_time = time.time()
        
        # Process each country
        for country in COUNTRIES:
            try:
                self.process_country(country)
            except Exception as e:
                print(f"\n✗ Error processing {country}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Verify indexing
        self.verify_indexing()
        
        elapsed = time.time() - start_time
        print(f"\nTotal time: {elapsed:.2f} seconds")
        print("="*60)


def main():
    """Entry point."""
    try:
        builder = IndexBuilder()
        builder.run()
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()