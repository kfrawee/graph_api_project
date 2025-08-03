# Graph API - Django + Celery

[![CI Pipeline](https://github.com/kfrawee/graph_api_project/actions/workflows/ci.yml/badge.svg)](https://github.com/kfrawee/graph_api_project/actions/workflows/ci.yml)

A Django REST API for graph operations with asynchronous path-finding using Celery.

## Features

- **CreateNode API**: Create nodes in the graph
- **ConnectNodes API**: Create directed connections between nodes
- **FindPath API**: Find shortest path between two nodes using BFS
- **SlowFindPath API**: Asynchronous path-finding with Celery
- **GetSlowPathResult API**: Retrieve results of asynchronous tasks

## Tech Stack

- **Backend**: Django 5.2.4 + Django REST Framework 3.16.0
- **Database**: PostgreSQL with psycopg2-binary
- **Cache/Message Broker**: Redis 6.2.0
- **Task Queue**: Celery 5.4.0
- **Environment Management**: django-environ
- **Code Quality**: Black, Ruff
- **Testing**: Pytest + pytest-django
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/kfrawee/graph_api_project.git
cd graph_api_project
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements/development.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your local settings
```

5. **Run with Docker Compose (Recommended)**
```bash
# Development environment
docker compose -f docker/docker-compose.dev.yml up --build

# Production environment
docker compose -f docker/docker-compose.prodyml up --build
```

6. **Or run locally**
```bash
# Start PostgreSQL and Redis (or use Docker services)
docker compose -f docker/docker-compose.dev.yml up db redis

# Run migrations
python manage.py migrate

# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A graph_api worker --loglevel=info
```

## API Endpoints

> You can find POSTMAN collection at: `/docs/Graph Node API.postman_collection.json`

### Base URL
```
http://localhost:8000/api/
```

### Health Check
```http
GET /api/health/
```

### Node Operations
```http
# Create a node
POST /api/nodes/create/
{
    "name": "NodeA"
}

# List all nodes
GET /api/nodes/
```

### Connection Operations
```http
# Connect two nodes
POST /api/nodes/connect/
{
    "from_node": "NodeA",
    "to_node": "NodeB"
}
```

### Path Finding
```http
# Find path (synchronous)
POST /api/path/find/
{
    "from_node": "NodeA",
    "to_node": "NodeC"
}

# Find path (asynchronous - returns task_id)
POST /api/path/slow-find/
{
    "from_node": "NodeA",
    "to_node": "NodeC"
}

# Get result of async path finding
GET /api/path/result/{task_id}/
```

## API Documentation

### CreateNode API
- **Endpoint**: `POST /api/nodes/create/`
- **Purpose**: Creates a new node with the given name
- **Request Body**: `{"name": "string"}`
- **Response**: Node details with timestamps
- **Status Codes**: 
  - 201: Node created successfully
  - 400: Invalid data or node already exists

### ConnectNodes API
- **Endpoint**: `POST /api/nodes/connect/`
- **Purpose**: Creates a directed connection from one node to another
- **Request Body**: `{"from_node": "string", "to_node": "string"}`
- **Response**: Connection confirmation
- **Status Codes**:
  - 201: Connection created successfully
  - 400: Invalid data, nodes don't exist, or connection already exists

### FindPath API
- **Endpoint**: `POST /api/path/find/`
- **Purpose**: Finds shortest path between two nodes using BFS algorithm
- **Request Body**: `{"from_node": "string", "to_node": "string"}`
- **Response**: `{"path": ["NodeA", "NodeB", "NodeC"] | null, "path_exists": boolean}`
- **Status Codes**:
  - 200: Always successful (path may be null if no connection exists)
  - 400: Invalid data or nodes don't exist

### SlowFindPath API
- **Endpoint**: `POST /api/path/slow-find/`
- **Purpose**: Initiates asynchronous path-finding (5-second delay simulation)
- **Request Body**: `{"from_node": "string", "to_node": "string"}`
- **Response**: `{"task_id": "string", "status": "PENDING"}`
- **Status Codes**:
  - 202: Task queued successfully
  - 400: Invalid data or nodes don't exist

### GetSlowPathResult API
- **Endpoint**: `GET /api/path/result/{task_id}/`
- **Purpose**: Retrieves result of asynchronous path-finding task
- **Response**: Task status and result (if completed)
- **Status Codes**:
  - 200: Task status retrieved (may be PENDING, SUCCESS, or FAILURE)
  - 404: Task not found

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest
```

### Run specific test files
```bash
pytest nodes/tests/test_models.py
pytest nodes/tests/test_views.py
pytest nodes/tests/test_services.py
pytest nodes/tests/test_tasks.py
```

### Run linting and formatting
```bash
# Check code formatting
black --check .

# Format code
black .

# Run linting
ruff check .

# Fix auto-fixable linting issues
ruff check . --fix
```

## Project Structure

```
graph_api_project/
├── .github/workflows/          # CI/CD workflows
├── docker/                     # Docker configuration
|── docs/                       # Contains useful documents (i.e Postman collection)
├── graph_api/                  # Django project settings
│   ├── settings/               # Environment-specific settings
│   ├── celery.py               # Celery configuration
│   └── urls.py                 # Root URL configuration
├── nodes/                      # Main application
│   ├── models.py               # Database models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── services.py             # Business logic
│   ├── tasks.py                # Celery tasks
│   ├── urls.py                 # App URL configuration
│   └── tests/                  # Test suite
├── requirements/               # Python dependencies
├── .env.example                # Environment variables template
├── manage.py                   # Django management script
└── README.md                   #  This file
```


### Development
```bash
# Build and start all services
docker-compose -f docker/docker-compose.dev.yml up --build

# Run migrations
docker-compose -f docker/docker-compose.dev.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker/docker-compose.dev.yml exec web python manage.py createsuperuser

# Run tests
docker-compose -f docker/docker-compose.dev.yml exec web pytest

# Access shell
docker-compose -f docker/docker-compose.dev.yml exec web python manage.py shell
```

### Production
```bash
# Build and start all services
docker-compose -f docker/docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f web

# Scale workers
docker-compose -f docker/docker-compose.prod.yml up --scale celery=3
```

---

## Example Usage

Here's a complete example of using the API:

```bash
# 1. Create nodes
curl -X POST http://localhost:8000/api/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "A"}'

curl -X POST http://localhost:8000/api/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "B"}'

curl -X POST http://localhost:8000/api/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "C"}'

# 2. Connect nodes (A -> B -> C)
curl -X POST http://localhost:8000/api/nodes/connect/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "A", "to_node": "B"}'

curl -X POST http://localhost:8000/api/nodes/connect/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "B", "to_node": "C"}'

# 3. Find path synchronously
curl -X POST http://localhost:8000/api/path/find/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "A", "to_node": "C"}'

# Response: {"path": ["A", "B", "C"], "path_exists": true}

# 4. Find path asynchronously
curl -X POST http://localhost:8000/api/path/slow-find/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "A", "to_node": "C"}'

# Response: {"task_id": "abc123...", "status": "PENDING"}

# 5. Get async result
curl http://localhost:8000/api/path/result/abc123.../

# Response: {"task_id": "abc123...", "status": "SUCCESS", "result": ["A", "B", "C"]}
```
---