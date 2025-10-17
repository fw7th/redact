<!--- FOR SVG (copied from starlette)
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Kludex/starlette/main/docs/img/starlette_dark.svg" width="420px">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Kludex/starlette/main/docs/img/starlette.svg" width="420px">
    <img alt="starlette-logo" src="https://raw.githubusercontent.com/Kludex/starlette/main/docs/img/starlette_dark.svg">
  </picture>
</p>

<p align="center">
    <em>✨ The little ASGI framework that shines. ✨</em>
</p>

---

-->


<div align="center">

<!---![Build Status](https://github.com/fw7th/redact/actions/workflows/ci.yml/badge.svg)--->
![Status](https://img.shields.io/badge/status-phase%204%20of%206-yellow)
![Build Status](https://github.com/fw7th/redact/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/fw7th/redact/badge.svg?branch=main)](https://coveralls.io/github/fw7th/redact?branch=main) </div>


<!---
---

**Documentation**: <a href="https://starlette.dev/" target="_blank">https://starlette.dev</a>

**Source Code**: <a href="https://github.com/Kludex/starlette" target="_blank">https://github.com/Kludex/starlette</a>

--->

---

# Redact
<p align="center">
 <em>A fast, containerized, and scalable API service for automated OCR and PII redaction on document batches.</em>
</p>

Redact is a production-ready microservice built with FastAPI that handles the secure and asynchronous processing of data redaction tasks. Designed to be easily deployed using Docker and scaled via a worker-based architecture (Redis/RQ setup).

Showcases:
- A robust, modern Python API using FastAPI (complete with automatic documentation).
- A clear separation of concerns (API, Core, Services, Workers).
- Scalable asynchronous task processing.
- Containerization with Docker.
- Database interaction via SQLAlchemy.

---

## Features
- RESTful API: Clear endpoints for submitting and retrieving redaction tasks.
- Asynchronous Processing: Long-running redaction tasks are handled by a dedicated worker pool, keeping the API fast and responsive.
- Persistent Storage: Uses SQLAlchemy for task metadata and Redis for task queuing.
- Containerized: Built for easy deployment with a Dockerfile.
- Benchmarked: Includes load testing scripts using Locust and benchmarks for performance analysis.

## 🚧 Project Status: [Phase 3 of 6]

Current: Making pytorch go `brrrrrr` i.e model creation
Next: Integration and testing (meh)

### Goal
Process batches of document images, automatically detect and redact sensitive information (PII).

## Architecture
<!-- TODO: Add diagram here once Phase 5 (integration) begins -->
[Diagram/description - update as you build #kinda lazy to do this one icl]

## Features
- [x] Batch image upload
- [x] Asynchronous processing
- [ ] Custom redaction model
- [ ] Enable batch prediction
- [ ] REST API
- [ ] Add auth
- [ ] Results retrieval
- [ ] Deploy to Docker/Kubernetes

## Phases
- [ ] Phase 1: Basic upload 
- [ ] Phase 2: Job tracking 
- [ ] Phase 3: Async infrastructure 
- [x] Phase 4: Model development (IN PROGRESS)
- [ ] Phase 5: Integration
- [ ] Phase 6: Deployment

## Tech Stack
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?style=flat-square&logo=fastapi)
![Uvicorn](https://img.shields.io/badge/ASGI%20Server-Uvicorn-FF9900?style=flat-square)

![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-D7174C?style=flat-square)
![Redis](https://img.shields.io/badge/Cache%20|%20Broker-Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![RQ](https://img.shields.io/badge/Job%20Queue-Python--RQ-A41E22?style=flat-square)

![PyTorch](https://img.shields.io/badge/ML%20Framework-PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Model](https://img.shields.io/badge/Model%20|%20OCR-Custom%20TBD-539165?style=flat-square)

![Docker](https://img.shields.io/badge/Containerization-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Orchestration-Compose-0062E5?style=flat-square&logo=docker&logoColor=white)

![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=flat-square)
![Linter](https://img.shields.io/badge/Linter-Ruff-663399?style=flat-square)
![Load Testing](https://img.shields.io/badge/Benchmarking-Locust-5CB53C?style=flat-square)

## Performance
[Add benchmarks as you build]
### API Benchmarking Table

| Endpoint              | Operation | Payload Size | Concurrent Users | Requests/sec | Avg Latency (ms) | P95 Latency (ms) | Error Rate | Notes                                      |
|-----------------------|-----------|--------------|------------------|---------------|------------------|------------------|------------|---------------------------------------------|
| `POST /predict`       | Create    | 1MB image     | 1                | 0.66          | 1450             | 1600             | 0%         | Includes file validation, disk write, Redis |
| `GET /predict/{id}`   | Read      | N/A           | 10               |               |                  |                  |            | Fetches job status from Redis               |
| `POST /items`         | Create    | 512B JSON     |                  |               |                  |                  |            | Basic DB insert                             |
| `GET /items/{id}`     | Read      | N/A           |                  |               |                  |                  |            | Add caching notes if applicable             |
| `PUT /items/{id}`     | Update    | 1KB JSON      |                  |               |                  |                  |            |                                             |
| `DELETE /items/{id}`  | Delete    | N/A           |                  |               |                  |                  |            |                                             |

> **Legend**:
> - *Payload Size*: Size of file or JSON sent in the request.
> - *Concurrent Users*: Simulated users (e.g., in Locust).
> - *Requests/sec*: Throughput under load.
> - *Latency*: Time from request to response (P95 = 95th percentile).


### Model Inference Benchmark Table
- [Model: TBD post Phase 4]

| Model Name         | Input Size        | Avg Inference Time (ms) | Throughput (req/sec) | Peak RAM Usage | Device | Notes                                  |
|--------------------|-------------------|--------------------------|-----------------------|----------------|--------|-----------------------------------------|
| `simulate_model_work` | N/A (simulated) | 30000 (sleep)            | 0.03                  | N/A            | CPU    | Simulated workload                      |
| `real_model.onnx`  | 224x224 image     |                          |                       |                | CPU    | Replace with real benchmark             |
| `resnet50`         | 512x512 image     |                          |                       |                | GPU    | ONNXRuntime on GPU                      |
| `custom_model.pt`  | Variable          |                          |                       |                | CPU/GPU| Fill in after deployment                |

> **Legend**:
> - *Inference Time*: Time to run prediction (ms).
> - *Throughput*: How many predictions/sec the model can handle.
> - *Peak RAM*: Max memory used during inference.
> - *Device*: CPU or GPU.

## 🔧 Quickstart
### Clone the repo
```bash
git clone https://github.com/yourname/redaction-api.git
cd redaction-api
```

### Create and activate virtualenv (optional)
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Copy example env and configure
```bash
cp .env.example .env
``````

### Start the app
```bash
uvicorn app.main:app --reload
```
 
### Client request example
```bash
curl -X POST http://localhost:8000/predict \
  -F "files=@cat.jpg"
```
#### Check job status
```bash
curl http://localhost:8000/predict/abc123
```

## Running tests
```bash
pytest tests/
```
### Optionally benchmark
./scripts/benchmark

## API Documentation
[Link to /docs once deployed]

When the server is running locally, visit:

- [http://localhost:8000/docs](http://localhost:8000/docs) — **Swagger UI**
- [http://localhost:8000/redoc](http://localhost:8000/redoc) — **ReDoc**

These provide interactive documentation of all available endpoints with live testing.

## Design Decisions
- `FastAPI`, mainly because it's lighter than Django.
- `Postgres`, I'm familiar with the dbms already, no need for any external onboarding.
- `Redis`: Read about persistence, speed, and distributed support. Decided to go with it over normal multiprocessing.Queue, it scales and it integrates well with Celery and RQ. Not using Kafka, or rabbit, project isn't that advanced.
- `RQ`: Initially wanted to use Celery, however after much investigation, I realized that it's probably too advanced for my use case. I'd rather avoid the setup overhead, just wanted simple and quick setup.

## Project Structure
Main directories and their purpose for anyone looking to understand or extend the codebase.

```text
redact/
├── benchmarks/         # Load testing and performance scripts (Locust, custom benchmarks)
├── redact/             # Main source code package
│   ├── api/            # FastAPI router definitions and main application entrypoint
│   ├── core/           # Configuration, logging, database/redis connection handling
│   ├── services/       # Business logic layer (e.g., storage abstraction)
│   ├── sqlschema/      # SQLAlchemy model definitions
│   └── workers/        # Asynchronous task processing logic (inference, main worker)
├── scripts/            # Helper scripts for development (benchmarking, service setup)
├── tests/              # Unit and integration tests (uses pytest)
└── requirements.txt    # All project dependencies

```

## Future Improvements
- [ ] Web UI
- [ ] Multiple output formats
- [x] Batch job scheduling

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
