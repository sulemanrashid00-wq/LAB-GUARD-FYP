# Month 3 — Backend Foundation, Database & Device Registration

**Project:** LabGuard-X: Autonomous Infrastructure Management & Security System  
**Lead / Backend Owner:** Muhammad Suleman  
**Deliverable Milestone:** M2 Foundation Gate (Operational Backend, Database, Auth & Device Registration)  

---

## 1. M2 Foundation Gate Verification Checklist

| Requirement / Milestone Goal | Status | Verification Evidence |
|---|---|---|
| **FastAPI Backend Server Running** | **COMPLETE** | `app.main:app` runs with CORS, OpenAPI at `/docs`, `/health` returns `200 OK` |
| **Database Connection & Resilient Fallback** | **COMPLETE** | Primary Supabase PostgreSQL connection with automated local SQLite fallback (`lab_guard.db`) |
| **Alembic Database Versioning** | **COMPLETE** | Migrations at head (`ba9c3de651b3`), unified `alembic.ini` for root and `backend/` |
| **S-03 Authentication & JWT Prototype** | **COMPLETE** | Register, Login, Me profile, Refresh token, and PBKDF2/bcrypt password hashing |
| **S-04 PC Device Registration API** | **COMPLETE** | `POST /api/v1/devices/register` persists PC hardware identities into database |
| **S-05 Telemetry & Heartbeat Ingestion** | **COMPLETE** | `POST /api/v1/agent/heartbeat` logs PC health (CPU/RAM/Disk) and liveliness |
| **Automated Verification Test Suite** | **COMPLETE** | 13/13 Pytest integration and functional tests passing |

---

## 2. Live API Endpoints Summary

### System & Health Endpoints
- `GET /` — API root status and banner
- `GET /health` — Operational health and active environment status
- `GET /docs` — Interactive OpenAPI Swagger UI documentation
- `GET /redoc` — Alternative ReDoc documentation

### S-03 Authentication Endpoints
- `POST /api/v1/auth/register` — New operator/student account registration
- `POST /api/v1/auth/login` — Issues access (`1440 min`) and refresh (`7 days`) tokens
- `GET /api/v1/auth/me` — Authenticated profile verification via Bearer token
- `POST /api/v1/auth/refresh` — Stateless access token renewal
- `POST /api/v1/auth/logout` — Session revocation acknowledgment

### S-04 Device Registry Endpoints
- `POST /api/v1/devices/register` — PC Agent automatic hardware registration
- `GET /api/v1/devices` — List registered devices with lab filtering & pagination
- `GET /api/v1/devices/{device_id}` — Retrieve device specifications and status
- `PATCH /api/v1/devices/{device_id}` — Update device state or assigned lab
- `DELETE /api/v1/devices/{device_id}` — Decommission device from registry

### S-05 Agent Heartbeat & Telemetry Endpoints
- `POST /api/v1/agent/heartbeat` — High-frequency agent heartbeat and PC health metrics
- `POST /api/v1/telemetry` — General hardware & environmental sensor telemetry
- `GET /api/v1/telemetry/device/{device_id}` — Historical telemetry time-series query
- `GET /api/v1/telemetry/device/{device_id}/latest` — Latest sensor snapshot
- `GET /api/v1/telemetry/device/{device_id}/summary` — Aggregate averages and metric peaks

---

## 3. Automated Test Verification Results

All automated test suites pass cleanly via `pytest backend/tests/ -v`:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.2.0

backend/tests/test_ai.py::test_ai_inference_and_analytics PASSED         [  7%]
backend/tests/test_alerts.py::test_create_and_manage_alert PASSED        [ 15%]
backend/tests/test_auth.py::test_register_user PASSED                    [ 23%]
backend/tests/test_auth.py::test_login_successful PASSED                 [ 30%]
backend/tests/test_auth.py::test_login_invalid_password PASSED           [ 38%]
backend/tests/test_auth.py::test_get_current_user_profile PASSED         [ 46%]
backend/tests/test_commands.py::test_issue_and_track_device_command PASSED [ 53%]
backend/tests/test_devices.py::test_create_and_list_device PASSED        [ 61%]
backend/tests/test_devices.py::test_update_device PASSED                 [ 69%]
backend/tests/test_devices.py::test_register_agent_device PASSED         [ 76%]
backend/tests/test_policies.py::test_policy_crud_and_enforcement PASSED  [ 84%]
backend/tests/test_telemetry.py::test_submit_and_query_telemetry PASSED  [ 92%]
backend/tests/test_telemetry.py::test_agent_heartbeat_and_telemetry PASSED [100%]

======================== 13 passed, 1 warning in 8.36s ========================
```

---

## 4. Runbook & Execution Instructions

```bash
# 1. Activate Virtual Environment
.\venv\Scripts\activate

# 2. Run Database Migrations to Latest Head
alembic upgrade head

# 3. Start Development Server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
