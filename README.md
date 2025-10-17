# Document Redaction System

> Automated OCR and PII redaction for document batches

# Document Redaction System

> Automated OCR and PII redaction for document batches

![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/framework-fastapi-green)
<!--- ![Build Status](https://github.com/fw7th/redact/actions/workflows/ci.yml/badge.svg)-->
![Coverage](https://coveralls.io/repos/github/fw7th/redact/badge.svg)
![Status](https://img.shields.io/badge/status-phase%203%20of%206-yellow)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 🚧 Project Status: [Phase 3 of 6]

Current: Making pytorch go `brrrrrr` i.e model creation
Next: Integration and testing (meh)

## Goal
Process batches of document images, automatically detect and redact sensitive information (PII).

## Architecture

<!-- TODO: Add diagram here once Phase 5 (integration) begins -->
> This project uses FastAPI for request handling, Redis + RQ for background job queues, and SQLModel for async DB operations. The model runs as a background task once files are uploaded.

[Diagram/description - update as you build #kinda lazy to do this one icl]

## Project Structure
redact/
├── api/                  # FastAPI application logic
│   └── main.py           # App entrypoint
├── benchmarks/           # Performance & load testing
│   ├── bench_predict.py
│   ├── locustfile.py
│   └── test_assets/      # Sample test images for benchmarking
├── core/                 # Core utilities (config, DB, logging, Redis)
│   ├── config.py
│   ├── database.py
│   ├── log.py
│   └── redis.py
├── services/             # Business logic and file handling
│   └── storage.py
├── sqlschema/            # SQLModel table definitions
│   └── tables.py
├── tests/                # Unit and integration tests
│   ├── conftest.py
│   ├── test_main.py
│   └── test_storage.py
├── workers/              # Background jobs and inference logic
│   ├── inference.py
│   └── worker.py
├── Dockerfile
└── README.md

## Features
- [x] Batch image upload
- [x] Asynchronous processing
- [ ] Custom redaction model
- [ ] REST API
- [ ] Results retrieval

## Phases
- [ ] Phase 1: Basic upload 
- [ ] Phase 2: Job tracking 
- [ ] Phase 3: Async infrastructure 
- [x] Phase 4: Model development (IN PROGRESS)
- [ ] Phase 5: Integration
- [ ] Phase 6: Deployment

## Tech Stack
- FastAPI
- PostgreSQL
- Redis
- RQ
- Docker
- [Model: TBD in Phase 4]

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
[Update each phase]

```bash
# Clone the repo
git clone https://github.com/yourname/redaction-api.git
cd redaction-api

# Create and activate virtualenv (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy example env and configure
cp .env.example .env

# Start the app
uvicorn app.main:app --reload
```

## API Documentation
[Link to /docs once deployed]

When the server is running locally, visit:

- [http://localhost:8000/docs](http://localhost:8000/docs) — **Swagger UI**
- [http://localhost:8000/redoc](http://localhost:8000/redoc) — **ReDoc**

These provide interactive documentation of all available endpoints with live testing.

## Design Decisions
- FastAPI, mainly because it's lighter than Django.
- Postgres, I'm familiar with the dbms already, no need for any external onboarding.
- Redis: Read about persistence, speed, and distributed support. Decided to go with it over normal multiprocessing.Queue, it scales and it integrates well with Celery and RQ. Not using Kafka, or rabbit, project isn't that advanced.
- RQ: Initially wanted to use Celery, however after much investigation, I realized that it's probably too advanced for my use case. I'd rather avoid the setup overhead, just wanted simple and quick setup.

## Future Improvements
- [ ] Web UI
- [ ] Multiple output formats
- [x] Batch job scheduling


## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
