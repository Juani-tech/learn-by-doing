# LearnByDoing Backend

Agentic backend for generating custom learning paths using LangGraph and GEMINI AI.

## Overview

This backend uses a multi-agent workflow with **real-time web search** to generate learning paths:

1. **Research Agent** - Searches the web (DuckDuckGo) for current topic information
2. **Curriculum Designer** - Creates learning structure + finds real documentation URLs
3. **Domain Expert** - Validates technical accuracy
4. **Quality Review** - Ensures "learn by doing" philosophy

The workflow loops until approved or max iterations reached (max 5).

### Key Features

- **Web Search Integration**: Uses DuckDuckGo to find current information (no API key needed!)
- **Real Documentation URLs**: Curates actual documentation links, not hallucinated URLs
- **Multi-Agent Validation**: 4 specialized agents ensure quality
- **Quality Gatekeeping**: Strict 0.85 threshold for "learn by doing" principles
- **PostgreSQL Persistence**: Full relational database with migrations
- **Async Architecture**: FastAPI with async database operations

## Quick Start

### Prerequisites

- Docker and Docker Compose
- GEMINI API key (get from https://open.bigmodel.cn/)

### Setup

1. **Clone and configure:**
```bash
cd learn-by-doing-backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

2. **Start with Docker:**
```bash
docker-compose up --build
```

3. **Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Manual Setup (without Docker)

1. **Install PostgreSQL** and create database
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run migrations:**
```bash
alembic upgrade head
```

4. **Start server:**
```bash
uvicorn app.main:app --reload
```

## API Usage

### Generate a Learning Path

```bash
curl -X POST http://localhost:8000/api/v1/paths/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Rust CLI tools",
    "context": "Want to build system utilities",
    "experience_level": "intermediate"
  }'
```

**Response:**
```json
{
  "pathId": "uuid-here",
  "path": { /* full learning path */ },
  "metadata": {
    "iterationCount": 3,
    "qualityScore": 0.92,
    "generationTimeSeconds": 85.4,
    "approved": true,
    "maxIterationsReached": false
  }
}
```

### Get a Path

```bash
curl http://localhost:8000/api/v1/paths/{path_id}
```

### List All Paths

```bash
curl http://localhost:8000/api/v1/paths
curl "http://localhost:8000/api/v1/paths?language=Rust"
```

## Architecture

### Agents

- **Research Agent** (`app/agents/research.py`): Discovers topic, use cases, prerequisites
- **Curriculum Agent** (`app/agents/curriculum.py`): Creates path structure with tasks
- **Expert Agent** (`app/agents/expert.py`): Validates technical accuracy
- **Quality Agent** (`app/agents/quality.py`): Gatekeeper for philosophy compliance

### Workflow

The LangGraph workflow (`app/workflow/graph.py`) orchestrates agents:

```
Research → Curriculum → Expert → Quality
                          ↓ (if rejected)
                    ← Loop back
                          ↓ (if approved)
                    Finalize
```

Max 5 iterations, quality threshold 0.85

### Database Schema

**learning_paths**: Path metadata and full JSON
**phases**: Phase structure
**tasks**: Individual tasks with requirements
**generation_jobs**: Track generation jobs

## Configuration

Environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Your GEMINI API key
- `GEMINI_MODEL`: Model to use (default: gemini-2.5-flash)
- `MAX_ITERATIONS`: Max workflow iterations (default: 5)
- `QUALITY_THRESHOLD`: Minimum quality score (default: 0.85)
- `VALIDATE_RESOURCES`: Check resource URLs (default: true)

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Test specific topic
python -c "
import asyncio
from app.services.path_service import PathService
from app.db.session import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        service = PathService(db)
        result = await service.generate_path('Rust CLI tools')
        print(f'Generated: {result[\"path_id\"]}')

asyncio.run(test())
"
```

## Development

### Adding New Agent

1. Create agent in `app/agents/`
2. Inherit from `BaseAgent`
3. Add to workflow in `app/workflow/graph.py`
4. Update tests

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Project Structure

```
learn-by-doing-backend/
├── app/
│   ├── api/           # FastAPI routes
│   ├── agents/        # LangGraph agents
│   ├── core/          # Config, LLM, logging
│   ├── db/            # Models and session
│   ├── services/      # Business logic
│   └── workflow/      # LangGraph workflow
├── alembic/           # Database migrations
├── docker/            # Docker configuration
├── tests/             # Test suite
└── docker-compose.yml
```

## Monitoring

Logs are structured JSON. Key metrics:
- Generation time
- Iteration count
- Quality scores
- Resource validation success rate

## License

MIT
