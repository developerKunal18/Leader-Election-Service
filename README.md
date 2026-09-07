# Leader Election Service

Flask project demonstrating lease-based leader election.

## Features
- Leader election
- 30-second leadership lease
- Same-node renewal
- Owner-only release
- Automatic expiration
- Thread-safe state
- Pytest tests

## Run
```bash
python -m venv .venv
pip install -r requirements.txt
python app.py
```

Endpoints:
- POST `/api/leader/acquire`
- POST `/api/leader/renew`
- POST `/api/leader/release`
- GET `/api/leader`
- GET `/health`

Run tests:
```bash
pytest
```

> Educational single-process simulation. Production systems should use a distributed coordination/consensus system.
