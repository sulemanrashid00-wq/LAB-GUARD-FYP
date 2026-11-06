# Lab Guard - Final Year Project (FYP)

Intelligent IoT and AI-driven Laboratory Environmental Monitoring, Safety Automation, and Access Control System.

## Project Structure
- [`backend/`](file:///e:/LAB%20GUARD-FYP/backend): Complete FastAPI + SQLAlchemy 2.0 + Pydantic v2 backend service.
  - `app/core/`: Application settings, security (JWT & password hashing), database sessions, and custom error handling.
  - `app/api/v1/`: Modular API endpoints (`auth`, `devices`, `telemetry`, `events`, `alerts`, `policies`, `commands`, `audit`, `iot`, `ai`).
  - `app/models/`: 12 relational database tables with full relationships.
  - `app/schemas/`: Pydantic request validation and response models.
  - `app/services/`: Business logic layer.
  - `migrations/`: Alembic database versioning scripts.
  - `tests/`: Automated unit & integration tests.

For full instructions, see [backend/README.md](file:///e:/LAB%20GUARD-FYP/backend/README.md).

