from fastapi import status


def test_submit_and_query_telemetry(client, user_token_headers, admin_token_headers):
    # Create device
    dev_res = client.post(
        "/api/v1/devices",
        headers=admin_token_headers,
        json={
            "name": "Temp & Humidity Sensor 01",
            "device_type": "sensor_node",
            "mac_address": "FE:DC:BA:98:76:54"
        }
    )
    device_id = dev_res.json()["data"]["id"]

    # Submit telemetry
    res_telem = client.post(
        "/api/v1/telemetry",
        headers=user_token_headers,
        json={
            "device_id": device_id,
            "temperature": 24.5,
            "humidity": 48.2,
            "gas_ppm": 120.0,
            "smoke_detected": False,
            "flame_detected": False,
            "motion_detected": True,
            "power_watts": 45.0,
            "sound_db": 38.5
        }
    )
    assert res_telem.status_code == status.HTTP_201_CREATED
    record = res_telem.json()["data"]
    assert record["temperature"] == 24.5
    assert record["device_id"] == device_id

    # Query device telemetry history
    res_hist = client.get(f"/api/v1/telemetry/device/{device_id}", headers=user_token_headers)
    assert res_hist.status_code == status.HTTP_200_OK
    assert len(res_hist.json()["data"]) >= 1

    # Query latest telemetry
    res_latest = client.get(f"/api/v1/telemetry/device/{device_id}/latest", headers=user_token_headers)
    assert res_latest.status_code == status.HTTP_200_OK
    assert res_latest.json()["data"]["temperature"] == 24.5

    # Query telemetry summary
    res_summary = client.get(f"/api/v1/telemetry/device/{device_id}/summary", headers=user_token_headers)
    assert res_summary.status_code == status.HTTP_200_OK
    assert res_summary.json()["data"]["avg_temperature"] == 24.5


def test_agent_heartbeat_and_telemetry(client):
    # 1. Register PC device first
    reg = client.post(
        "/api/v1/devices/register",
        json={
            "device_id": "PC-TEST-HB-01",
            "hostname": "PC-HEALTH-NODE",
            "ip": "192.168.1.188",
            "os": "Windows 11",
            "agent_version": "1.0.0"
        }
    )
    assert reg.status_code == status.HTTP_201_CREATED

    # 2. Post Heartbeat with CPU, RAM, Disk telemetry
    hb = client.post(
        "/api/v1/agent/heartbeat",
        json={
            "device_id": "PC-TEST-HB-01",
            "timestamp": "2026-11-06T19:50:00Z",
            "agent_version": "1.0.0",
            "agent_status": "running",
            "health": {
                "cpu_pct": 22.4,
                "ram_pct": 58.1,
                "disk_used_pct": 64.0,
                "disk_total_gb": 512.0
            }
        }
    )
    assert hb.status_code == status.HTTP_201_CREATED
    assert hb.json()["success"] is True

    # 3. Post Heartbeat for non-registered device (should fail with 404)
    hb_fail = client.post(
        "/api/v1/agent/heartbeat",
        json={
            "device_id": "PC-NOT-FOUND",
            "timestamp": "2026-11-06T19:50:00Z",
            "agent_version": "1.0.0",
            "agent_status": "running"
        }
    )
    assert hb_fail.status_code == status.HTTP_404_NOT_FOUND


