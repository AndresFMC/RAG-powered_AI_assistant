# RAG Powered AI Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Serverless-success.svg)](https://www.pinecone.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Intelligent employment regulations assistant using RAG (Retrieval-Augmented Generation) architecture with namespace isolation to provide accurate, country-specific answers from a private knowledge base.

## Live Demo

**Frontend:** [https://rag-powered-ai-assistant-frontend.s3.eu-central-1.amazonaws.com/index.html](https://rag-powered-ai-assistant-frontend.s3.eu-central-1.amazonaws.com/index.html)

**API Endpoint:** `https://sycfgthg0g.execute-api.eu-central-1.amazonaws.com/prod/query`

Experience real-time RAG technology with namespace-isolated knowledge retrieval across 5 countries. API access requires authentication key (provided to evaluators separately).

---

## Problem Statement

Organizations operating across multiple countries face challenges accessing accurate, jurisdiction-specific employment regulations. Traditional documentation systems:
- Mix information from different countries
- Lack contextual understanding
- Require manual cross-referencing
- Cannot synthesize information from multiple sources

**Result:** Time-consuming research, potential compliance errors, and difficulty accessing accurate country-specific guidance.

---

## Solution

A serverless RAG system with **namespace isolation** that ensures zero cross-contamination between countries:

1. **Select Country** - Choose from 5 supported jurisdictions
2. **Ask Question** - Natural language queries about employment regulations
3. **Get Answer** - Contextual responses with source citations from the correct country
4. **Verify Sources** - Review document references with relevance scores

The system uses **Pinecone namespaces** to guarantee that queries to Spain only retrieve Spanish documents, Poland only Polish documents, etc.

---

## Architecture

The system consists of two distinct phases: **Index Building** (offline, one-time) and **Query Runtime** (online, per request).

### Phase 1: Index Building (Offline)

```mermaid
graph TB
    subgraph "Data Source"
        A[PDF Documents<br/>15 files, 5 countries]
    end
    
    subgraph "build_index.py Script"
        B[IndexBuilder.init]
        B --> C[get_vector_store<br/>Factory: Pinecone]
        B --> D[get_embeddings<br/>Factory: Titan v2]
        B --> E[RecursiveTextSplitter<br/>chunk: 1000, overlap: 200]
    end
    
    subgraph "Processing Pipeline"
        F[PyPDFLoader<br/>Load PDFs]
        G[text_splitter.split<br/>Generate chunks]
        H[Add metadata<br/>country, file, page]
        I[embed_query<br/>Per chunk]
    end
    
    subgraph "AWS Bedrock"
        J[Titan v2<br/>1024 dimensions]
    end
    
    subgraph "Vector Preparation"
        K[Prepare vectors<br/>id, values, metadata]
        L[vector_store.upsert<br/>Batch by namespace]
    end
    
    subgraph "Pinecone Namespaces"
        M1[spain: 49 vectors]
        M2[poland: 46 vectors]
        M3[colombia: 49 vectors]
        M4[italy: 44 vectors]
        M5[georgia: 43 vectors]
    end
    
    A --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M1
    L --> M2
    L --> M3
    L --> M4
    L --> M5
    
    style M1 fill:#fee
    style M2 fill:#efe
    style M3 fill:#fef
    style M4 fill:#eff
    style M5 fill:#ffe
```

### Phase 2: Query Runtime (Online)

```mermaid
graph TB
    subgraph "User Interface"
        A[User: select country<br/>+ enter question]
        B[S3 Static Frontend<br/>index.html]
    end
    
    subgraph "AWS Infrastructure"
        C[API Gateway<br/>API Key validation<br/>Rate limiting]
        D[Lambda Container<br/>2048MB, 300s timeout]
    end
    
    subgraph "RAGPipeline.query Method"
        E[Step 1: Validate country]
        F[Step 2: embeddings.embed_query<br/>Question → vector]
        G[Step 3: vector_store.search<br/>Query namespace]
        H[Step 4: Extract chunks<br/>+ metadata]
        I[Step 5: llm.generate_with_context<br/>Question + Context]
        J[Step 6: Format response<br/>answer + sources + metadata]
    end
    
    subgraph "AWS Bedrock"
        K[Titan v2<br/>Embedding generation]
        L[Claude 3.5 Sonnet<br/>Answer generation]
    end
    
    subgraph "Pinecone Query"
        M{Namespace<br/>Router}
        N1[spain namespace]
        N2[poland namespace]
        N3[colombia namespace]
        N4[italy namespace]
        N5[georgia namespace]
        O[Top-K results<br/>default: 5]
    end
    
    A --> B
    B -->|POST + x-api-key| C
    C --> D
    D --> E
    E --> F
    F --> K
    K --> G
    G --> M
    M -->|country=spain| N1
    M -->|country=poland| N2
    M -->|country=colombia| N3
    M -->|country=italy| N4
    M -->|country=georgia| N5
    N1 --> O
    N2 --> O
    N3 --> O
    N4 --> O
    N5 --> O
    O --> H
    H --> I
    I --> L
    L --> J
    J --> D
    D --> C
    C --> B
    B --> A
    
    style N1 fill:#fee
    style N2 fill:#efe
    style N3 fill:#fef
    style N4 fill:#eff
    style N5 fill:#ffe
```

### Technical Stack

| Component | Technology | Configuration |
|-----------|-----------|---------------|
| **Frontend** | S3 Static Website | HTML/CSS/JS, HTTPS enabled |
| **API** | API Gateway REST | CORS enabled, API key protected |
| **Compute** | Lambda Container Image | Python 3.12, 2048MB, 300s timeout |
| **Orchestration** | Custom RAG Core | Factory pattern, cloud-agnostic design |
| **Vector DB** | Pinecone Serverless | 1024 dims, cosine similarity, us-east-1 |
| **Embeddings** | Bedrock Titan v2 | amazon.titan-embed-text-v2:0 |
| **LLM** | Bedrock Claude 3.5 Sonnet | anthropic.claude-3-5-sonnet-20240620-v1:0 |
| **Monitoring** | CloudWatch Logs | Lambda execution logs |

---

## Key Features

### Namespace Isolation
**Critical requirement:** Zero cross-contamination between countries.
- Each country has its own Pinecone namespace
- Queries to Spain only search `spain` namespace
- **Test results:** 100% isolation verified across all countries

### Performance
- **Cold start:** 7-8.5s (Lambda container initialization)
- **Warm start:** 2.5-3s (subsequent requests)
- **Vector search:** ~300ms (Pinecone serverless)
- **LLM generation:** ~2.1s (Claude 3.5 Sonnet)

### Accuracy
- Top-5 relevant chunks retrieved per query
- Cosine similarity scoring
- Source citations with page numbers and relevance scores
- Context-grounded answers (reduces hallucinations)

### Scalability
- Serverless architecture (auto-scaling)
- 231 vectors across 5 namespaces
- Supports thousands of concurrent queries
- No infrastructure management required

### Security
- AWS API Gateway key authentication
- Rate limiting: 200 requests/day per key
- Burst protection: 20 req/sec, sustained 10 req/sec
- CloudWatch monitoring and logging

---

## Supported Countries

| Country | Documents | Vector Count | Namespace |
|---------|-----------|--------------|-----------|
| Spain | 3 PDFs | 49 chunks | `spain` |
| Poland | 3 PDFs | 46 chunks | `poland` |
| Colombia | 3 PDFs | 49 chunks | `colombia` |
| Italy | 3 PDFs | 44 chunks | `italy` |
| Georgia | 3 PDFs | 43 chunks | `georgia` |

**Total:** 15 PDF documents, 231 indexed chunks

---

## Project Structure

```
RAG-powered_AI_assistant/
├── rag_core/                       # Cloud-agnostic modular architecture
│   ├── config/
│   │   └── settings.py            # Centralized configuration
│   ├── interfaces/                # Abstract contracts (swap components easily)
│   │   ├── vector_store.py        # Abstract VectorStore
│   │   ├── llm.py                 # Abstract LLM
│   │   └── embeddings.py          # Abstract Embeddings
│   ├── implementations/           # Concrete providers (Pinecone, Bedrock)
│   │   ├── vector_stores/
│   │   │   └── pinecone_store.py  # Pinecone implementation
│   │   ├── llms/
│   │   │   └── bedrock_llm.py     # Bedrock LLM implementation
│   │   └── embeddings/
│   │       └── bedrock_embeddings.py
│   ├── factories/                 # Component selection logic
│   │   ├── vector_store_factory.py
│   │   ├── llm_factory.py
│   │   └── embeddings_factory.py
│   └── core/
│       └── rag_pipeline.py        # Main RAG orchestration
├── lambda_function/
│   ├── app.py                     # Lambda handler
│   ├── Dockerfile                 # Container image
│   └── requirements.txt           # Lambda dependencies
├── scripts/
│   ├── build_index.py             # Index PDFs to Pinecone
│   └── deploy_frontend.sh         # Deploy frontend to S3
├── frontend/
│   └── index.html                 # Web interface
├── data/                          # PDF documents by country
│   ├── spain/
│   ├── poland/
│   ├── colombia/
│   ├── italy/
│   └── georgia/
├── test_results.md                # Comprehensive test report
├── requirements.txt               # Development dependencies
├── .env                           # Environment variables (not in repo)
├── .gitignore
├── LICENSE
└── README.md
```

---

## Installation & Deployment

### Prerequisites

- AWS Account with Bedrock access in `eu-central-1`
- Pinecone account (free tier)
- Python 3.12+
- Docker Desktop (for Lambda container)
- AWS CLI configured

### 1. Clone Repository

```bash
git clone https://github.com/AndresFMC/RAG-powered_AI_assistant.git
cd RAG-powered_AI_assistant
```

### 2. Set Up Python Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file:
```bash
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=rag-powered-ai-assistant

# AWS Configuration (auto-detected by Lambda)
AWS_REGION=eu-central-1

# Bedrock Models
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v2:0
BEDROCK_LLM_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0

# Component Selection
VECTOR_STORE_TYPE=pinecone
EMBEDDINGS_TYPE=bedrock
LLM_TYPE=bedrock

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

### 4. Create Pinecone Index

```bash
# Via Pinecone Console:
# - Name: rag-powered-ai-assistant
# - Dimension: 1024 (Titan v2)
# - Metric: cosine
# - Cloud: AWS
# - Region: us-east-1 (free tier)
```

### 5. Index Documents to Pinecone

```bash
# Ensure PDFs are in data/{country}/ directories
python scripts/build_index.py
```

**Output:** 231 vectors indexed across 5 namespaces (~2-3 minutes)

### 6. Build and Deploy Lambda Container

```bash
# Build Docker image (M1 Mac: use --platform linux/amd64)
cd RAG-powered_AI_assistant
docker build --platform linux/amd64 \
  -f lambda_function/Dockerfile \
  -t rag-powered-ai-assistant:latest .

# Authenticate to ECR
aws ecr get-login-password --region eu-central-1 | \
  docker login --username AWS --password-stdin \
  {ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com

# Tag and push
docker tag rag-powered-ai-assistant:latest \
  {ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com/rag-powered-ai-assistant:latest
docker push {ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com/rag-powered-ai-assistant:latest

# Create Lambda function
aws lambda create-function \
  --function-name rag-powered-ai-assistant \
  --package-type Image \
  --code ImageUri={ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com/rag-powered-ai-assistant:latest \
  --role {LAMBDA_ROLE_ARN} \
  --environment Variables="{PINECONE_API_KEY=...,PINECONE_INDEX_NAME=...}" \
  --timeout 300 \
  --memory-size 2048 \
  --region eu-central-1
```

### 7. Create API Gateway with API Key Protection

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "rag-powered-ai-assistant-api" \
  --region eu-central-1

# Create API Key
aws apigateway create-api-key \
  --name "rag-demo-key" \
  --enabled \
  --region eu-central-1

# Create Usage Plan with rate limits
aws apigateway create-usage-plan \
  --name "rag-demo-plan" \
  --throttle burstLimit=20,rateLimit=10 \
  --quota limit=200,period=DAY \
  --region eu-central-1

# Associate API key to usage plan and stage
# (See full deployment commands in deployment documentation)
```

**Note:** Complete API Gateway setup includes creating resources, methods, integrations, and CORS configuration. The API will require `x-api-key` header for all requests.

### 8. Deploy Frontend

```bash
# Update frontend/index.html with your API endpoint
# Deploy to S3
./scripts/deploy_frontend.sh
```

---

## Security & Authentication

The API is protected by **AWS API Gateway API Keys** with infrastructure-level rate limiting.

### Rate Limits

| Limit Type | Value |
|------------|-------|
| Requests per day | 200 |
| Burst rate | 20 req/sec |
| Sustained rate | 10 req/sec |

### Authentication Flow

1. User enters API key in frontend
2. Frontend includes key in `x-api-key` header
3. API Gateway validates key before routing to Lambda
4. Invalid/missing keys receive 403 Forbidden

### Why API Gateway Keys?

This implementation demonstrates:
- **Infrastructure-level security** via AWS native services
- **Rate limiting** to prevent abuse and control costs
- **Key rotation** capability without code changes
- **Usage tracking** and monitoring via CloudWatch

### Production Considerations

For production deployments, consider:
- Backend proxy to hide keys from client
- OAuth 2.0 / JWT authentication
- Per-user quotas and throttling
- Key expiration policies

---

## API Usage

### Endpoint
```
POST https://sycfgthg0g.execute-api.eu-central-1.amazonaws.com/prod/query
```

**Authentication:** All requests require `x-api-key` header.

### Request Format

```json
{
  "country": "spain",
  "question": "What is the probation period in Spain?"
}
```

**Supported countries:** `spain`, `poland`, `colombia`, `italy`, `georgia`

### Response Format

```json
{
  "answer": "According to the context provided, the probation period in Spain varies depending on the employee's qualifications:\n\n1. For qualified technicians with a university degree: Up to 6 months.\n2. For all other employees: Up to 2 months...",
  "country": "spain",
  "sources": [
    {
      "file": "02_spain_labor_regulations.pdf",
      "score": 0.5056,
      "page": 2.0
    },
    {
      "file": "01_spain_general_hiring_guide.pdf",
      "score": 0.4298,
      "page": 2.0
    }
  ],
  "chunks_used": 5,
  "model": "anthropic.claude-3-5-sonnet-20240620-v1:0"
}
```

### Example with cURL

```bash
curl -X POST \
  "https://sycfgthg0g.execute-api.eu-central-1.amazonaws.com/prod/query" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY_HERE" \
  -d '{"country":"poland","question":"What are the mandatory vacation days?"}'
```

### Stats Endpoint

```bash
curl -X POST \
  "https://sycfgthg0g.execute-api.eu-central-1.amazonaws.com/prod/query" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY_HERE" \
  -d '{"action":"stats"}'
```

**Response:**
```json
{
  "total_vectors": 231,
  "namespaces": {
    "spain": {"vector_count": 49},
    "poland": {"vector_count": 46},
    "colombia": {"vector_count": 49},
    "italy": {"vector_count": 44},
    "georgia": {"vector_count": 43}
  },
  "countries": ["spain", "poland", "colombia", "italy", "georgia"]
}
```

### Error Responses

**403 Forbidden** (Invalid or missing API key):
```json
{
  "message": "Forbidden"
}
```

**400 Bad Request** (Missing required fields):
```json
{
  "error": "Missing required fields: country and question"
}
```

---

## Testing Results

See [test_results.md](test_results.md) for comprehensive test report.

### Key Findings

**Namespace Isolation:** 100% verified
- Spain queries return only Spanish documents
- Poland queries return only Polish documents
- Zero cross-contamination across all 5 countries

**Performance Metrics:**
- Cold start: 4.75s (within target)
- Warm start: 2.92s (excellent)
- Vector search: ~300ms
- End-to-end: <5s average

**Error Handling:**
- Invalid country: ✓ Proper error message
- Empty question: ✓ Validation works
- Irrelevant questions: ✓ Acknowledges lack of context

---

## Architecture Decisions

### Why Pinecone Serverless?

**Requirement:** Guarantee zero cross-contamination between countries.

**Evaluation:**
- **Graph DB:** Adds complexity without addressing isolation need
- **SQL Database:** Not optimized for vector similarity search
- **Pinecone Namespaces:** Native isolation at infrastructure level

**Decision:** Pinecone with namespace-per-country architecture ensures impossible cross-contamination while maintaining cloud-agnostic design.

### Why No SQL Database?

**Evaluation:** The requirements mentioned SQL for "tax rates" as a potential use case.

**Analysis:**
- **No structured data in scope:** The knowledge base consists of PDF documents (unstructured text)
- **No tax calculations required:** Queries are informational ("What is X?"), not computational ("Calculate tax for...")
- **Vector DB sufficient:** All information retrievable via semantic search

**Decision:** SQL database would add complexity without providing value for this use case. If future requirements include:
- Structured tax rate tables for dynamic calculations
- Relational queries across countries
- Financial computations

Then SQL (PostgreSQL) can be integrated via the existing factory pattern without refactoring the core architecture.

**Prepared for extension:** The modular design allows adding SQL alongside vector and graph databases as needed.

### Why Lambda Container Image?

**Challenge:** Dependencies exceed 250MB Lambda layer limit.

**Solution:** Container image deployment (10GB limit vs 250MB).

**Benefits:**
- Same environment local and deployed
- Reproducible builds
- Easier dependency management

### Why Modular Architecture?

**Design:** Factory pattern with 3-layer architecture (Application → Interface → Implementation)

**Benefits:**
- Swap Pinecone for Qdrant: Change 1 config line
- Swap Bedrock for vLLM: Change 1 config line
- Business logic untouched
- Cloud-agnostic: No vendor lock-in
- Production-ready from day 1


---

## Cost Analysis

### Development Costs
- **Pinecone:** Free tier (sufficient for PoC)
- **Bedrock:** Free tier + minimal usage (~$2)
- **Lambda:** Free tier
- **API Gateway:** Free tier
- **S3:** <$0.10/month

**Total PoC cost:** ~$2-3

### Production Estimates (1000 queries/month)

| Component | Cost/Month |
|-----------|------------|
| Pinecone free tier | $0 |
| Bedrock Titan embeddings | ~$0.30 |
| Bedrock Claude 3.5 | ~$2.50 |
| Lambda | ~$0.20 |
| API Gateway | ~$0.10 |
| S3 | ~$0.10 |
| **Total** | **~$3.20** |

**Per query:** ~$0.003

---

## Limitations & Future Enhancements

### Current Limitations
1. **Fixed countries:** 5 hardcoded countries (not dynamic namespace creation)
2. **Single API key tier:** No per-user quotas or tiered access
3. **No caching:** Every query hits full RAG pipeline
4. **English only:** UI and responses in English
5. **No conversation history:** Stateless queries only

### Planned Enhancements
- Dynamic country/namespace management
- Per-user authentication with tiered access
- Response caching (Redis/ElastiCache)
- Multi-language support
- Conversation context and history
- Advanced analytics dashboard
- Graph DB integration for relationship queries

---

## Troubleshooting

### Lambda Issues

**Cold start >10s:**
- Check container image size
- Verify Lambda memory (2048MB recommended)
- Review CloudWatch logs for initialization errors

**Import errors:**
```bash
# Verify dependencies match
pip freeze > requirements.txt
# Rebuild container
docker build --no-cache ...
```

### Pinecone Issues

**Connection errors:**
- Verify API key in environment variables
- Check index name matches configuration
- Confirm region is us-east-1 (free tier)

**Dimension mismatch:**
```
Error: Vector dimension 1024 does not match index 1536
```
**Solution:** Recreate index with dimension=1024

### API Gateway Issues

**403 Forbidden:**
- Verify API key is valid and enabled
- Check usage plan association
- Confirm API deployed to correct stage

**CORS errors:**
- Verify OPTIONS method configured
- Check CORS headers in Lambda response
- Confirm API deployed to `prod` stage

**404 Not Found:**
- Verify API endpoint URL
- Check resource path: `/query`
- Confirm Lambda integration configured

---

## Development

### Local Testing

```bash
# Test RAG pipeline locally
python test_rag_local.py

# Expected output:
# RAG Pipeline initialized
# Countries: ['spain', 'poland', ...]
# Query test passed
```

### Update Frontend

```bash
# Edit frontend/index.html
# Deploy changes
./scripts/deploy_frontend.sh
```

### Rebuild Index

```bash
# Add new PDFs to data/{country}/
# Reindex
python scripts/build_index.py
```

---

## Contributing

Contributions welcome! Areas for improvement:
- Additional countries/jurisdictions
- Enhanced authentication system
- Caching layer
- Multi-language support
- Advanced search filters

Please open an issue before starting major work.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contact

**Andres F.**
- LinkedIn: [linkedin.com/in/andres-fmc](https://www.linkedin.com/in/andres-fmc/)
- GitHub: [github.com/AndresFMC](https://github.com/AndresFMC)

---

**Built with:** AWS Lambda • Amazon Bedrock • Pinecone • Python 3.12