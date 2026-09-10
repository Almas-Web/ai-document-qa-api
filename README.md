# AI Document Q&A API

A RAG-based Document Q&A API built with FastAPI, PostgreSQL, pgvector, local embeddings, and Gemini.

Users can upload PDF documents, extract and chunk their content, generate local vector embeddings, and ask questions using Retrieval-Augmented Generation (RAG).

## Features

* JWT authentication
* User registration and login
* Protected API endpoints
* User-specific document ownership
* PDF text extraction
* Text chunking with overlap
* Local embeddings with Sentence Transformers
* PostgreSQL with pgvector
* Vector similarity search
* Retrieval-Augmented Generation (RAG)
* Gemini LLM integration
* Document listing
* Document deletion
* Alembic database migrations
* Dockerized PostgreSQL + pgvector
* Pytest API testing

## Tech Stack

* Python 3.11+
* FastAPI
* PostgreSQL
* pgvector
* SQLAlchemy
* Alembic
* Sentence Transformers
* Gemini API
* JWT
* Docker
* Pytest

## Architecture

```text
                    ┌─────────────────┐
                    │     Client      │
                    │ Swagger / API   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │      API        │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌───────────────┐             ┌───────────────┐
      │ PDF Processing│             │ Authentication │
      │ & Chunking    │             │     JWT       │
      └───────┬───────┘             └───────────────┘
              │
              ▼
      ┌───────────────────┐
      │ Local Embeddings  │
      │ all-MiniLM-L6-v2  │
      └─────────┬─────────┘
                │
                ▼
      ┌───────────────────┐
      │ PostgreSQL +      │
      │ pgvector          │
      └─────────┬─────────┘
                │
          User Question
                │
                ▼
      ┌───────────────────┐
      │ Vector Similarity │
      │ Search            │
      └─────────┬─────────┘
                │
                ▼
      ┌───────────────────┐
      │ Relevant Context  │
      └─────────┬─────────┘
                │
                ▼
      ┌───────────────────┐
      │ Gemini LLM        │
      └─────────┬─────────┘
                │
                ▼
          Final Answer
```

## RAG Workflow

```text
PDF Upload
    ↓
Extract Text
    ↓
Split Text into Chunks
    ↓
Generate Local Embeddings
    ↓
Store Chunks + Embeddings
    ↓
User Asks Question
    ↓
Generate Question Embedding
    ↓
pgvector Similarity Search
    ↓
Retrieve Relevant Chunks
    ↓
Send Context + Question to Gemini
    ↓
Generate Grounded Answer
```

## Project Structure

```text
ai-document-qa-api/
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   └── documents.py
│   ├── core/
│   │   └── security.py
│   ├── db/
│   │   ├── database.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── chunk.py
│   │   ├── document.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── chunk.py
│   │   ├── document.py
│   │   └── qa.py
│   ├── services/
│   │   ├── chunk_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── gemini_service.py
│   │   ├── pdf_service.py
│   │   └── retrieval_service.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_api.py
├── uploads/
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Authentication

The API uses JWT-based authentication.

### Register

```http
POST /auth/register
```

Request:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

### Login

```http
POST /auth/login
```

Request:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

The response contains an access token.

Use the token in Swagger:

```text
Bearer <access_token>
```

### Current User

```http
GET /auth/me
```

Returns the currently authenticated user.

## Document API

### Upload Document

```http
POST /documents/upload
```

Accepts a PDF file.

The API:

1. Saves the PDF
2. Extracts text
3. Splits the text into chunks
4. Generates embeddings
5. Stores the document
6. Stores the chunks and embeddings

Example response:

```json
{
  "id": 1,
  "filename": "example.pdf",
  "text_length": 10068,
  "chunk_count": 23,
  "embedding_dimension": 384
}
```

### List Documents

```http
GET /documents/
```

Returns documents belonging to the authenticated user.

### Ask a Question

```http
POST /documents/ask
```

Request:

```json
{
  "document_id": 1,
  "question": "What is an LLM?"
}
```

The API performs vector similarity search and sends the most relevant chunks to Gemini.

Example response:

```json
{
  "question": "What is an LLM?",
  "answer": "..."
}
```

### Delete Document

```http
DELETE /documents/{document_id}
```

Deletes:

* Document record
* Associated chunks
* Uploaded PDF file

Users can only access and delete their own documents.

## Embeddings

The project uses the local Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The embedding dimension is:

```text
384
```

Embeddings are generated locally, so document embeddings do not require a paid embedding API.

## Vector Search

Document embeddings are stored in PostgreSQL using pgvector.

For a user question:

```text
Question
   ↓
Question Embedding
   ↓
pgvector Cosine Similarity
   ↓
Top Relevant Chunks
```

The retrieved chunks are then provided to Gemini as context.

## Gemini Integration

Gemini is used only for answer generation.

The model receives:

```text
Relevant Document Context
+
User Question
```

The system instructs the model to answer using the provided document context.

If the answer cannot be found in the retrieved context, the API instructs the model to indicate that the answer was not found in the document.

## Database Models

```text
users
  │
  │ 1 ─────── N
  ▼
documents
  │
  │ 1 ─────── N
  ▼
chunks
```

### Users

Stores:

* User ID
* Email
* Hashed password
* Creation timestamp

### Documents

Stores:

* Document ID
* Owner user ID
* Filename
* Text length
* Chunk count
* Creation timestamp

### Chunks

Stores:

* Chunk ID
* Document ID
* Chunk content
* Vector embedding
* Creation timestamp

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://postgres:postgres@localhost:5445/document_qa
JWT_SECRET_KEY=your_secret_key
```

Never commit `.env` to GitHub.

For other developers, use `.env.example`:

```env
GEMINI_API_KEY=
DATABASE_URL=
JWT_SECRET_KEY=
```

## Database Setup

The project uses Docker only for PostgreSQL with pgvector.

Start the database:

```bash
docker compose up -d
```

Check the container:

```bash
docker ps
```

The database is exposed on:

```text
localhost:5445
```

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Migration

Run:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

## Run the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## API Endpoints

| Method | Endpoint                   | Description                 |
| ------ | -------------------------- | --------------------------- |
| POST   | `/auth/register`           | Register user               |
| POST   | `/auth/login`              | Login and get JWT           |
| GET    | `/auth/me`                 | Get current user            |
| POST   | `/documents/upload`        | Upload PDF                  |
| GET    | `/documents/`              | List user's documents       |
| POST   | `/documents/ask`           | Ask question about document |
| DELETE | `/documents/{document_id}` | Delete document             |

## Testing

Run the test suite:

```bash
pytest
```

Current tests cover the basic API health endpoint, with additional authentication, document, ownership, and RAG tests planned as the project is finalized.

## Error Handling

The API handles common validation and authentication errors, including:

* Missing filename
* Unsupported file type
* Empty PDF
* Invalid authentication token
* Expired authentication token
* Invalid login credentials
* Empty questions
* Missing documents
* Unauthorized document access

## Security

* Passwords are hashed before storage.
* JWT tokens are used for authentication.
* Protected endpoints require authentication.
* Users can only access their own documents.
* Gemini API credentials are stored in environment variables.
* Database credentials are stored in environment variables.
* `.env` is excluded from version control.

## Current Status

Implemented:

* FastAPI application
* PDF processing
* Text chunking
* Local embeddings
* PostgreSQL
* pgvector
* Vector similarity search
* Gemini integration
* RAG pipeline
* JWT authentication
* Protected endpoints
* Document ownership
* Document listing
* Document deletion
* Alembic migrations
* Docker PostgreSQL setup
* Basic pytest setup

## Future Improvements

* More comprehensive automated tests
* Streaming LLM responses
* Conversation history
* Improved chunking strategies
* Reranking
* Metadata filtering
* Background document processing with Celery
* Qdrant integration
* Production deployment
* CI/CD pipeline improvements
* Better document retrieval evaluation

