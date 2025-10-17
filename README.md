# Document Redaction System

> Automated OCR and PII redaction for document batches

## 🚧 Project Status: [Phase 3 of 6]

Current: Building basic upload infrastructure
Next: Adding job tracking database

## Goal
Process batches of document images, automatically detect and redact sensitive information (PII).

## Architecture
[Diagram/description - update as you build #kinda lazy to do this one icl]

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

## Getting Started
[Update each phase]

## API Documentation
[Link to /docs once deployed]

## Design Decisions
- FastAPI, mainly because it's lighter than Django.
- Postgres, I'm familiar with the dbms already, no need for any external onboarding.
- Redis: Read about persistence, speed, and distributed support. Decided to go with it over normal multiprocessing.Queue, it scales and it integrates well with Celery and RQ. Not using Kafka, or rabbit, project isn't that advanced.
- RQ: Initially wanted to use Celery, however after much investigation, I realized that it's probably too advanced for my use case. I'd rather avoid the setup overhead, just wanted simple and quick setup.

## Future Improvements
- [ ] Web UI
- [ ] Multiple output formats
- [x] Batch job scheduling
