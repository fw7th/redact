<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
<div align="center">

[![YT-DLP](https://raw.githubusercontent.com/fw7th/redact/main/.github/redact-logo.svg)](#readme)

![Status](https://img.shields.io/badge/status-phase%204%20of%206-yellow?style=for-the-badge)
![Build Status](https://github.com/fw7th/redact/actions/workflows/ci.yml/badge.svg?style=for-the-badge)
[![Coverage Status](https://coveralls.io/repos/github/fw7th/redact/badge.svg?branch=main&style=for-the-badge)](https://coveralls.io/github/fw7th/redact?branch=main) </div>

<!-- MANPAGE: END EXCLUDED SECTION -->

<p align="center">
 <em>A fast, containerized, and scalable API service for automated OCR and PII redaction on document batches.</em>
</p>

Redact is a production-ready microservice built with FastAPI that handles the secure and asynchronous processing of data redaction tasks. Designed to be easily deployed using Docker and scaled via a worker-based architecture (Redis/RQ setup).

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->

### Features
- RESTful API: Clear endpoints for submitting and retrieving redaction tasks.
- Asynchronous Processing: Long-running redaction tasks are handled by a dedicated worker pool, keeping the API fast and responsive.
- Persistent Storage: Uses SQLAlchemy for task metadata and Redis for task queuing.
- Containerized: Built for easy deployment with a Dockerfile.
- Benchmarked: Includes load testing scripts using Locust and benchmarks for performance analysis.

<!-- MANPAGE: END EXCLUDED SECTION -->


<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
### Performance

#### API Benchmarking Table

| Endpoint              | Operation | Payload Size | Concurrent Users | Requests/sec | Avg Latency (ms) | P95 Latency (ms) | Error Rate | Notes                                      |
|-----------------------|-----------|--------------|------------------|---------------|------------------|------------------|------------|---------------------------------------------|
| `POST /predict`             | Create    | 100KB image   | 2                | 0.67          | 34.95            | 56               | 0%         | Includes file validation, disk write, Redis, ML model inference |
| `GET /download/{id}`        | GET       | N/A           | 10               | 3.58          | 10.38            | 32               | 0%         |Retrieve processed document from server                          |
| `GET /check/{id}`           | Read      | N/A           | 10               | 3.52          | 9.94             | 28               | 0%         | Fetches job status from Redis                                   |
| `DELETE /drop/{id}`         | Delete    | N/A           | 10               | 3.47          | 10.43            | 30               |            | Delete a batch and all related files from DB                    |

- **Legend**:
> - *Payload Size*: Size of file or JSON sent in the request.
> - *Concurrent Users*: Simulated users (e.g., in Locust).
> - *Requests/sec*: Throughput under load.
> - *Latency*: Time from request to response (P95 = 95th percentile).


#### Model Inference Benchmark Table
> [Models]
- [NER: GLiNER (Medium v2.1 {Remember to cite urchade and the GLiNER paper})]
- [OCR: Tesseract 5.5.1 w/ py-tesseract]

| Model Name         | Input Size        | Avg Inference Time (ms)     | Device | Notes                                   |
|--------------------|-------------------|-----------------------------|--------|-----------------------------------------|
| `GLiNER v2.1`      | 200 lines of text | 790                         | CPU    | Model has a long cold start 20secs-ish  |
| `Tesseract`        | 512x512 image     | 0.96                        | CPU    | Tesseract?                              |

- **Legend**:
> - *Inference Time*: Time to run prediction (ms).
> - *Throughput*: How many predictions/sec the model can handle.

> *Tests performed in a subprocess.*


### Quickstart
#### Clone the repo
```bash
git clone https://github.com/fw7th/redact.git
cd redact
```

#### Create and activate virtualenv (optional)
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Copy example env and configure
```bash
cp .env.example .env
``````

#### Start the app
```bash
uvicorn app.main:app --reload
```
 
#### Client request example
```bash
curl -X POST http://localhost:8000/predict \
  -F "files=@cat.jpg"
```
#### Check job status
```bash
curl http://localhost:8000/predict/abc123
```

#### Running tests
```bash
pytest tests/
```
#### Optionally benchmark
```bash
./scripts/benchmark
```

### API Documentation
[Link to /docs once deployed]

When the server is running locally, visit:

- [http://localhost:8000/docs](http://localhost:8000/docs) — **Swagger UI**
- [http://localhost:8000/redoc](http://localhost:8000/redoc) — **ReDoc**

These provide interactive documentation of all available endpoints with live testing.

### License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

### Citations
- [GLiNER](https://github.com/fw7th/GLiNER) was pivotal in the development of the PII redaction module.
@misc{stepanov2024glinermultitaskgeneralistlightweight,
      title={GLiNER multi-task: Generalist Lightweight Model for Various Information Extraction Tasks}, 
      author={Ihor Stepanov and Mykhailo Shtopko},
      year={2024},
      eprint={2406.12925},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2406.12925}, 
}

- Tesseract, the OCR engine, performs text extraction in this project.
@Manual{,
  title = {tesseract: Open Source OCR Engine},
  author = {Jeroen Ooms},
  year = {2026},
  note = {R package version 5.2.5},
  url = {https://docs.ropensci.org/tesseract/},
}
