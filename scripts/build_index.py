"""
Build Index Script - RAG Powered AI Assistant
Indexes PDF documents into Pinecone with namespace isolation per country.
Integrated with LangSmith for monitoring.
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
import boto3

# Load environment variables
load_dotenv()

# LangSmith configuration
if os.getenv('LANGSMITH_TRACING') == 'true':
    print(f"✓ LangSmith tracing enabled")
    print(f"  Endpoint: {os.getenv('LANGSMITH_ENDPOINT')}")
    print(f"  Project: {os.getenv('LANGSMITH_PROJECT')}")

# Configuration
COUNTRIES = ['spain', 'poland', 'colombia', 'italy', 'georgia']
DATA_DIR = Path('data')
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_DIMENSION = 1024  # Titan v2 generates 1024 dimensions

class IndexBuilder:
    def __init__(self):
        """Initialize Pinecone and Bedrock clients."""
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index_name = os.getenv('PINECONE_INDEX_NAME')
        
        # Get or create index
        self.index = self._get_or_create_index()
        
        # Initialize Bedrock embeddings
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'eu-central-1')
        )
        
        embedding_model = 'amazon.titan-embed-text-v2:0'
        
        self.embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id=embedding_model
        )
        
        # Verify embedding dimensions
        print(f"Using embedding model: {embedding_model}")
        test_embedding = self.embeddings.embed_query("test")
        print(f"Embedding dimensions: {len(test_embedding)}")
        
        if len(test_embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Expected {EMBEDDING_DIMENSION} dimensions, got {len(test_embedding)}. "
                f"Index is configured for {EMBEDDING_DIMENSION} dimensions."
            )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✓ IndexBuilder initialized")
    
    def _get_or_create_index(self):
        """Get existing index or create if it doesn't exist."""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating new index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=EMBEDDING_DIMENSION,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            time.sleep(10)
        
        return self.pc.Index(self.index_name)
    
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
        """Generate embeddings and upsert to Pinecone."""
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
                # Generate embedding
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
            
            # Upsert to Pinecone
            self.index.upsert(
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
        
        stats = self.index.describe_index_stats()
        
        print(f"\nIndex: {self.index_name}")
        print(f"Total vectors: {stats.total_vector_count}")
        print(f"\nNamespace breakdown:")
        
        for namespace, ns_stats in stats.namespaces.items():
            print(f"  • {namespace}: {ns_stats.vector_count} vectors")
        
        # Check if all countries are present
        missing = set(COUNTRIES) - set(stats.namespaces.keys())
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
        raise


if __name__ == "__main__":
    main()