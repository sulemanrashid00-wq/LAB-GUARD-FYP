# Month 2 — SRS, Database Design & API Contracts

**Project:** LabGuard-X: Autonomous Infrastructure Management & Security System  
**Lead / Backend Owner:** Muhammad Suleman  
**Deliverable Milestone:** API Contracts, RBAC Specification, Database Schemas, and SRS Alignment  

---

## 1. Authentication & Role-Based Access Control (RBAC — S-03)

The backend provides stateless JSON Web Token (JWT) authentication using HMAC-SHA256 (`HS256`).

### Roles Matrix
- **`admin` / `superadmin`**: Full system privileges, device provisioning, policy creation, remote command dispatch, audit logs.
- **`operator`**: Operational triage, device status view, alert acknowledgment, command execution.
- **`teacher`**: Lab policy enforcement (Exam Mode), attendance, read-only incident access.
- **`student`**: Profile inspection, read-only authorized lab access.

---

## 2. API Contracts & Payload Specifications

### S-04: Device / PC Agent Registration
- **Endpoint:** `POST /api/v1/devices/register`
- **Auth:** Public (Device initialization)
- **Request Payload:**
```json
{
  "device_id": "PC-LAB1-001",
  "hostname": "DESKTOP-CHEM01",
  "ip": "192.168.1.101",
  "os": "Windows 11 Pro 64-bit",
  "agent_version": "1.0.0"
}
```
- **Success Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Device registered successfully",
  "data": {
    "device_id": "PC-LAB1-001",
    "hostname": "DESKTOP-CHEM01",
    "ip": "192.168.1.101",
    "os": "Windows 11 Pro 64-bit",
    "agent_version": "1.0.0",
    "status": "offline",
    "registered_at": "2026-11-06T13:30:00Z"
  }
}
```

---

### S-05: PC Agent Heartbeat & Health Telemetry
- **Endpoint:** `POST /api/v1/agent/heartbeat`
- **Auth:** Public / Device Identity
- **Request Payload:**
```json
{
  "device_id": "PC-LAB1-001",
  "timestamp": "2026-11-06T13:35:00Z",
  "agent_version": "1.0.0",
  "agent_status": "running",
  "health": {
    "cpu_pct": 24.5,
    "ram_pct": 58.2,
    "disk_used_pct": 61.4,
    "disk_total_gb": 512.0
  }
}
```
- **Success Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Heartbeat and telemetry processed successfully"
}
```
- **Error Response — Unregistered Device (`404 Not Found`):**
```json
{
  "detail": "Device is not registered yet."
}
```

---

### S-06: Security & Compliance Events Ingestion
- **Endpoint:** `POST /api/v1/events`
- **Auth:** Bearer Token
- **Request Payload:**
```json
{
  "lab_id": 1,
  "device_id": "PC-LAB1-001",
  "event_type": "unauthorized_usb_plugged",
  "severity": "high",
  "description": "Mass storage device Kingston DataTraveler detected during Exam Mode.",
  "metadata_json": {
    "vendor_id": "0951",
    "product_id": "1666",
    "serial_number": "001A920B"
  }
}
```
- **Success Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Event recorded successfully",
  "data": {
    "id": 101,
    "lab_id": 1,
    "device_id": "PC-LAB1-001",
    "event_type": "unauthorized_usb_plugged",
    "severity": "high",
    "created_at": "2026-11-06T13:36:00Z"
  }
}
```

---

### S-08: Incident Alerts & Triage
- **Endpoint:** `GET /api/v1/alerts?status=active`
- **Auth:** Bearer Token
- **Success Response (`200 OK`):**
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "lab_id": 1,
      "title": "Unauthorized Storage Device Detected",
      "severity": "high",
      "status": "active",
      "created_at": "2026-11-06T13:36:05Z"
    }
  ]
}
```

---

### S-09: Remote Commands Dispatch
- **Endpoint:** `POST /api/v1/commands`
- **Auth:** Bearer Token (Admin / Operator)
- **Request Payload:**
```json
{
  "device_id": "PC-LAB1-001",
  "command_type": "lock_screen",
  "payload_json": { "reason": "Exam Mode Violation" }
}
```
- **Success Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Command queued for device execution",
  "data": {
    "id": 12,
    "device_id": "PC-LAB1-001",
    "command_type": "lock_screen",
    "status": "pending",
    "created_at": "2026-11-06T13:37:00Z"
  }
}
```

---

## 3. Standardized Error Envelope
All error responses adhere to standard HTTP status codes and unified JSON schema:
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Device with ID 'PC-UNKNOWN' does not exist",
    "timestamp": "2026-11-06T13:38:00Z"
  }
}
```
