<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fw7th/redact/main/.github/redact_light.svg" width="420px">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/fw7th/redact/main/.github/redact.svg" width="420px">
    <img alt="redact-logo" src="https://raw.githubusercontent.com/fw7th/redact/main/.github/redact.svg">
  </picture>
</p>

<p align="center">
 <em>🔒 A fast, serverless, and scalable API service for automated OCR and PII redaction on document batches.</em>
</p>

---

<!-- MANPAGE: END EXCLUDED SECTION -->

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->

<div align="center">

![Release](https://img.shields.io/github/v/release/fw7th/redact?style=for-the-badge)
![Build Status](https://img.shields.io/github/actions/workflow/status/fw7th/redact/ci.yml?branch=main&style=for-the-badge)
[![Coverage Status](https://img.shields.io/coveralls/github/fw7th/redact/main?style=for-the-badge)](https://coveralls.io/github/fw7th/redact?branch=main)

</div>

Redact exposes a [FastAPI HTTPs](https://fastapi.tiangolo.com/) interface, persists state in [Supabase (Postgres + Storage)](https://supabase.com/), and offloads compute-heavy redaction workloads to [Modal](https://modal.com/)

<!-- MANPAGE: END EXCLUDED SECTION -->

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->

### Features
- RESTful API: Clear endpoints for submitting and retrieving redaction tasks.
- Asynchronous Processing: Long-running redaction jobs are executed asynchronously via serverless compute.
- Persistent Storage: Task metadata stored in Supabase Postgres via SQLAlchemy; documents stored in Supabase Storage.
- Benchmarked: Includes load testing scripts using Locust and benchmarks for performance analysis.

- **API**: FastAPI
- **Database**: Supabase Postgres
- **Object Storage**: Supabase Storage
- **Compute**: Modal (serverless execution)

<!-- MANPAGE: END EXCLUDED SECTION -->

<p align="center">
  <img src="https://raw.githubusercontent.com/fw7th/redact/main/assets/test.jpg" width="300" alt="Random image" />
  <img src="https://raw.githubusercontent.com/fw7th/redact/main/assets/test_redacted.jpg" width="300" alt="Redacted image" />
</p>

<p align="center"><em>Random image I found on the internet vs. Redacted.</em></p>


<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
### Performance

#### API Benchmarking Table

| Endpoint              | Operation | Payload Size | Concurrent Users | Requests/sec | Avg Latency (ms) | P95 Latency (ms) | Error Rate | Notes                                      |
|-----------------------|-----------|--------------|------------------|---------------|------------------|------------------|------------|---------------------------------------------|
| `POST /predict`             | Create    | 100KB image   | 2                | 0.67          | 34.95            | 56               | 0%         | Includes file validation, disk write, Inference offshoring      |
| `GET /download/{id}`        | GET       | N/A           | 10               | 3.58          | 10.38            | 32               | 0%         |Retrieve processed document from server                          |
| `GET /check/{id}`           | Read      | N/A           | 10               | 3.52          | 9.94             | 28               | 0%         | Fetches job status from Supabase Postgres                       |
| `DELETE /drop/{id}`         | Delete    | N/A           | 10               | 3.47          | 10.43            | 30               |            | Delete a batch and all related files from DB                    |

> ***Legend***:
> - *Payload Size*: Size of file or JSON sent in the request.
> - *Concurrent Users*: Simulated users (e.g., in Locust).
> - *Requests/sec*: Throughput under load.
> - *Latency*: Time from request to response (P95 = 95th percentile).

<!-- MANPAGE: END EXCLUDED SECTION -->

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->

### Usage
To interact with the hosted service as a client, see the [`client/`](client/) directory for example request scripts and helpers.

> ⚠️ Local execution note  
> Running the API locally is intended for development and testing only.  
> Production workloads are designed to run on Modal’s serverless infrastructure.

### Development Setup

#### Prerequisites
To run this project locally, you will need:

1. **A Supabase project**
   - Supabase Postgres (used for task metadata)
   - Supabase Storage (used for document and redaction artifacts)

2. **A Modal account**
   - Modal must be configured locally (one-time setup)

3. **Python 3.10+**

#### Modal Authentication
Modal must be authenticated on your local machine.

If you have not configured Modal before, run:

```bash
modal token set
```
This will store your credentials locally (e.g. in ~/.modal.toml).
Alternatively, you may provide credentials manually via environment variables:

```env
MODAL_TOKEN_ID=...
MODAL_TOKEN_SECRET=...
```

Ensure the Modal app name configured in the project is unique within your Modal account.

Supabase credentials are always required.
Modal credentials are optional if Modal is already configured locally. You only need to set your modal app name in the .env file.

Then from ~/redact/ proceed to run:
```python
modal run redact/workers/modalapp.py 
```

For a persistent app on modal run:
```python
modal deploy redact/workers/modalapp.py 
```

### Quickstart
#### Clone the repo
```bash
git clone https://github.com/fw7th/redact.git
cd redact
```

#### Create and activate virtualenv (optional)
```bash
python -m venv venv
source venv/bin/activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Copy example env and configure
Please go over the `Development Setup` Prerequisites section.
```bash
cp .env.example .env
```

#### Start the app
```bash
uvicorn app.main:app --reload
```

#### Running tests
```bash
pytest tests/
```

#### Optionally benchmark
```bash
./benchmark/benchmark
```

This project does not use Docker for deployment; serverless execution is handled entirely by Modal.

<!-- MANPAGE: END EXCLUDED SECTION -->

#### API Documentation

When the server is running locally, visit:

- [http://localhost:8000/docs](http://localhost:8000/docs) — **Swagger UI**
- [http://localhost:8000/redoc](http://localhost:8000/redoc) — **ReDoc**

These provide interactive documentation of all available endpoints with live testing.

### License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

### Citations
- [GLiNER medium v2.1](https://github.com/fw7th/GLiNER) was pivotal in the development of the PII redaction module.
```bibtex
@misc{stepanov2024glinermultitaskgeneralistlightweight,
      title={GLiNER multi-task: Generalist Lightweight Model for Various Information Extraction Tasks}, 
      author={Ihor Stepanov and Mykhailo Shtopko},
      year={2024},
      eprint={2406.12925},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2406.12925}, 
}
```

- [Tesseract v5.5.1 w/ py-tesseract](https://github.com/tesseract-ocr/tesseract), the Open Source OCR engine, performs text extraction in this project.

```bibtex
@Manual{,
  title = {tesseract: Open Source OCR Engine},
  author = {Jeroen Ooms},
  year = {2026},
  note = {R package version 5.2.5},
  url = {https://docs.ropensci.org/tesseract/},
}
```
