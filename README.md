# LabGuard-X — Autonomous Infrastructure Management & Security System

Intelligent IoT and AI-driven Laboratory Environmental Monitoring, Safety Automation, and Access Control System (Final Year Project).

---

## 📁 Repository Structure

- [`backend/`](file:///e:/LAB%20GUARD-FYP/backend): Complete FastAPI + SQLAlchemy 2.0 + Pydantic v2 backend service.
  - `app/core/`: Application settings (`config.py`), security (`security.py`), database engine (`database.py`), and error handlers (`errors.py`).
  - `app/api/v1/`: Modular REST routers (`auth`, `devices`, `telemetry`, `events`, `alerts`, `policies`, `commands`, `audit`, `iot`, `ai`).
  - `app/models/`: 12 SQLAlchemy ORM relational database models.
  - `app/schemas/`: Pydantic request/response validation schemas.
  - `app/services/`: Encapsulated business logic layer.
  - `tests/`: Automated test suite (13/13 passing).
- [`migrations/`](file:///e:/LAB%20GUARD-FYP/migrations): Single source of truth for Alembic database migrations.
- [`docs/`](file:///e:/LAB%20GUARD-FYP/docs): Project milestone documentation and handoff contracts:
  - [`Month 1 — Architecture Baseline & Scope`](file:///e:/LAB%20GUARD-FYP/docs/MONTH_1_ARCHITECTURE_AND_BASELINE.md)
  - [`Month 2 — API Contracts & SRS Alignment`](file:///e:/LAB%20GUARD-FYP/docs/MONTH_2_API_CONTRACTS_AND_SRS.md)
  - [`Month 3 — Deliverables, Runbook & Verification`](file:///e:/LAB%20GUARD-FYP/docs/MONTH_3_DELIVERABLES_AND_VERIFICATION.md)

---

## 🚀 Quickstart

```bash
# 1. Activate Virtual Environment
.\venv\Scripts\activate

# 2. Run Database Migrations
alembic upgrade head

# 3. Start Server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Test Verification

Run the complete test suite:
```bash
pytest backend/tests/ -v
```
*(All 13 test suites pass cleanly.)*
