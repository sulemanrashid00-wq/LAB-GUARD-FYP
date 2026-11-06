# Lab Guard FYP - Intelligent Lab Monitoring & Security Backend

A modern, production-ready, asynchronous backend architecture for **Lab Guard** — an intelligent Internet of Things (IoT) and Artificial Intelligence (AI) driven platform for laboratory environmental monitoring, safety automation, access control, and incident mitigation.

---

## 📁 Project Architecture & Sequence

The codebase is organized in the following clean, modular structure:

```
backend/
├── app/
│   ├── main.py                  # FastAPI application lifecycle, middleware, error handlers, and router mount
│   ├── core/                    # Core infrastructure: config, security, database session, custom errors
│   │   ├── config.py            # Pydantic Settings configuration from .env
│   │   ├── database.py          # SQLAlchemy engine, session maker, declarative Base, and get_db dependency
│   │   ├── security.py          # JWT generation, PBKDF2 hashing, user & IoT API key auth dependencies
│   │   └── errors.py            # Custom application exceptions and standardized global JSON handlers
│   ├── api/v1/                  # RESTful API routers (10 domains)
│   │   ├── api.py               # Aggregated APIRouter combining all endpoints
│   │   ├── auth.py              # User authentication, registration, JWT login, and profile
│   │   ├── devices.py           # Device lifecycle, hardware registry, status, and CRUD
│   │   ├── telemetry.py         # Ingestion and time-series query of temperature, gas, smoke, flame, motion
│   │   ├── events.py            # Safety incident event logging and querying
│   │   ├── alerts.py            # Incident alerts, triage, acknowledgment, and resolution workflows
│   │   ├── policies.py          # Laboratory threshold rules and dynamic automation policies
│   │   ├── commands.py          # Remote device actuation commands (smart locks, buzzers, relays)
│   │   ├── audit.py             # Security audit logs of all privileged operations
│   │   ├── iot.py               # Hardware gateway endpoints (heartbeat, telemetry ingest, command ack)
│   │   └── ai.py                # AI anomaly detection, hazard scoring, and ML analytics
│   ├── models/                  # SQLAlchemy 2.0 ORM models (12 Tables)
│   │   ├── user.py              # 1. users
│   │   ├── lab.py               # 2. labs
│   │   ├── device.py            # 3. devices
│   │   ├── device_config.py     # 4. device_configs
│   │   ├── telemetry.py         # 5. telemetry_records
│   │   ├── event.py             # 6. events
│   │   ├── alert.py             # 7. alerts
│   │   ├── policy.py            # 8. policies
│   │   ├── command.py           # 9. device_commands
│   │   ├── audit.py             # 10. audit_logs
│   │   ├── ai_inference.py      # 11. ai_inferences
│   │   └── access_log.py        # 12. access_logs
│   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── auth.py              # Auth and token schemas
│   │   ├── user.py              # User schemas
│   │   ├── lab.py               # Lab schemas
│   │   ├── device.py            # Device and hardware config schemas
│   │   ├── telemetry.py         # Sensor reading schemas
│   │   ├── event.py             # Event schemas
│   │   ├── alert.py             # Alert schemas
│   │   ├── policy.py            # Policy rule schemas
│   │   ├── command.py           # Remote command schemas
│   │   ├── audit.py             # Audit log schemas
│   │   ├── iot.py               # IoT gateway ingestion schemas
│   │   ├── ai.py                # AI inference and hazard prediction schemas
│   │   └── common.py            # Generic API wrappers and paginated response models
│   └── services/                # Business logic layer
│       ├── auth_service.py      # User credential verification and token creation
│       ├── device_service.py    # Hardware provisioning and status synchronization
│       ├── telemetry_service.py # Time-series sensor ingestion and metric calculations
│       ├── event_service.py     # Incident capture and classification
│       ├── alert_service.py     # Alert creation, assignment, and resolution
│       ├── policy_service.py    # Rule engine evaluating telemetry against thresholds
│       ├── command_service.py   # Hardware command queueing and execution state
│       ├── audit_service.py     # Immutable activity tracking
│       ├── iot_service.py       # Hardware protocol abstraction (ESP32/Raspberry Pi)
│       └── ai_service.py        # Anomaly scoring and predictive hazard analytics
├── migrations/                  # Alembic database migrations
│   ├── env.py                   # Migration environment linking SQLAlchemy models
│   ├── script.py.mako           # Migration template
│   └── versions/
│       └── 0001_initial_schema.py # Complete migration script for all 12 tables
├── tests/                       # Automated tests (pytest)
│   ├── conftest.py              # In-memory SQLite fixtures, client, and test users
│   ├── test_auth.py             # Auth endpoint tests
│   ├── test_devices.py          # Device CRUD tests
│   ├── test_telemetry.py        # Sensor telemetry tests
│   ├── test_alerts.py           # Alert lifecycle tests
│   ├── test_policies.py         # Policy threshold tests
│   ├── test_commands.py         # Remote command tests
│   └── test_ai.py               # AI inference tests
├── .env.example                 # Environment variables template
├── requirements.txt             # Python package dependencies
└── README.md                    # Project documentation
```

---

## 🗄️ Database Schema (12 Core Tables)

1. **`users`**: Administrative and operator accounts (`id`, `username`, `email`, `role`, `hashed_password`, `is_active`).
2. **`labs`**: Physical laboratory facilities and rooms (`id`, `name`, `code`, `building`, `room_number`, `capacity`).
3. **`devices`**: Registered IoT nodes, microcontrollers, and smart sensors (`id`, `lab_id`, `name`, `device_type`, `mac_address`, `api_key`, `status`).
4. **`device_configs`**: Hardware sampling frequencies, reporting intervals, and sensitivity settings (`id`, `device_id`, `sampling_rate_sec`, `config_json`).
5. **`telemetry_records`**: Time-series sensor readings (`id`, `device_id`, `temperature`, `humidity`, `gas_ppm`, `smoke_detected`, `flame_detected`, `motion_detected`, `power_watts`, `sound_db`).
6. **`events`**: Environmental and security events (`id`, `lab_id`, `device_id`, `event_type`, `severity`, `description`).
7. **`alerts`**: Actionable incident tickets requiring operator intervention (`id`, `lab_id`, `title`, `severity`, `status`, `acknowledged_by`, `resolved_by`).
8. **`policies`**: Dynamic safety rules and automatic thresholds (`id`, `lab_id`, `name`, `rule_type`, `condition_operator`, `threshold_value`, `action_type`).
9. **`device_commands`**: Instructions dispatched to IoT hardware (`id`, `device_id`, `command_type`, `payload_json`, `status`, `response_json`).
10. **`audit_logs`**: Tamper-evident trail of all privileged administrative actions (`id`, `user_id`, `action`, `resource_type`, `resource_id`, `ip_address`).
11. **`ai_inferences`**: Multi-sensor anomaly detection and predictive hazard scores (`id`, `lab_id`, `model_name`, `confidence_score`, `is_anomaly`, `prediction_output_json`).
12. **`access_logs`**: RFID, PIN, and biometric physical entrance events (`id`, `lab_id`, `user_id`, `access_method`, `access_status`, `card_uid`).

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Virtual Environment tool (`venv` or `conda`)

### 2. Setup Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
*(By default, SQLite is pre-configured, so no external database installation is required for local development.)*

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Alternative Documentation (ReDoc)**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 7. Run Automated Tests
```bash
pytest -v
```

---

## 🔐 Default Credentials (Initial Seed)
When the application starts for the first time, it automatically provisions the following default superadmin:

- **Username / Email**: `admin@labguard.local`
- **Password**: `Admin@123456`
- **Role**: `superadmin`

*(Remember to change the default credentials and secret key before deploying to production!)*

