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

## 🚧 Project Status: [Phase 5 of 6]

Current: Integration and testing

### Goal
Process batches of document images, automatically detect and redact sensitive information (PII).

## Features
- [x] Batch image upload
- [x] Asynchronous processing
- [x] Redaction model
- [x] Enable batch prediction
- [x] REST API
- [x] Results retrieval
- [ ] Deploy to Docker/Kubernetes

## Phases
- [ ] Phase 1: Basic upload 
- [ ] Phase 2: Job tracking 
- [ ] Phase 3: Async infrastructure 
- [ ] Phase 4: Model development (IN PROGRESS)
- [x] Phase 5: Integration
- [ ] Phase 6: Deployment

## Performance
### API Benchmarking Table

| Endpoint              | Operation | Payload Size | Concurrent Users | Requests/sec | Avg Latency (ms) | P95 Latency (ms) | Error Rate | Notes                                      |
|-----------------------|-----------|--------------|------------------|---------------|------------------|------------------|------------|---------------------------------------------|
| `POST /predict`             | Create    | 100KB image   | 2                | 0.67          | 34.95            | 56               | 0%         | Includes file validation, disk write, Redis, ML model inference |
| `GET /download/{id}`        | GET       | N/A           | 10               | 3.58          | 10.38            | 32               | 0%         |Retrieve processed document from server                          |
| `GET /check/{id}`           | Read      | N/A           | 10               | 3.52          | 9.94             | 28               | 0%         | Fetches job status from Redis                                   |
| `DELETE /drop/{id}`         | Delete    | N/A           | 10               | 3.47          | 10.43            | 30               |            | Delete a batch and all related files from DB                    |

> **Legend**:
> - *Payload Size*: Size of file or JSON sent in the request.
> - *Concurrent Users*: Simulated users (e.g., in Locust).
> - *Requests/sec*: Throughput under load.
> - *Latency*: Time from request to response (P95 = 95th percentile).


### Model Inference Benchmark Table
- [Models]
- [NER: GLiNER (Medium v2.1 {Remember to cite urchade and the GLiNER paper})]
- [OCR: Tesseract 5.5.1 w/ py-tesseract]

| Model Name         | Input Size        | Avg Inference Time (ms)     | Device | Notes                                   |
|--------------------|-------------------|-----------------------------|--------|-----------------------------------------|
| `GLiNER v2.1`      | 200 lines of text | 790                         | CPU    | Model has a long cold start 20secs-ish  |
| `Tesseract`        | 512x512 image     | 0.96                        | CPU    | Tesseract?                              |

> **Legend**:
> - *Inference Time*: Time to run prediction (ms).
> - *Throughput*: How many predictions/sec the model can handle.

> *Tests performed in a subprocess.*


## Quickstart
### Clone the repo
```bash
git clone https://github.com/fw7th/redact.git
cd redact
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
uvicorn redact.app:app --reload
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

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
