### Hosted API

You can interact with the hosted Redact service at:

**Base URL:**  
[https://redact-api.vercel.app](https://redact-api.vercel.app)

**Available Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| POST   | `/predict` | Submit documents for OCR and PII redaction |
| GET    | `/check/{id}` | Check the status of a submitted job |
| GET    | `/download/{id}` | Download the redacted document |
| DELETE | `/drop/{id}` | Delete a batch and all related files |

**API Documentation:**  
- Swagger UI: [https://redact-api.vercel.app/docs](https://redact-api.vercel.app/docs)  
- ReDoc: [https://redact-api.vercel.app/redoc](https://redact-api.vercel.app/redoc)


More information is relayed in the the post and delete files.
