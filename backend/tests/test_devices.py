from fastapi import status


def test_create_and_list_device(client, admin_token_headers):
    # Register device
    res_create = client.post(
        "/api/v1/devices",
        headers=admin_token_headers,
        json={
            "name": "ESP32 Gas & Flame Node 1",
            "device_type": "sensor_node",
            "mac_address": "AA:BB:CC:DD:EE:01",
            "ip_address": "192.168.1.150",
            "firmware_version": "1.0.4",
            "config": {
                "sampling_rate_sec": 5,
                "reporting_interval_sec": 30,
                "sensitivity": "high"
            }
        }
    )
    assert res_create.status_code == status.HTTP_201_CREATED
    dev_data = res_create.json()["data"]
    assert dev_data["name"] == "ESP32 Gas & Flame Node 1"
    assert dev_data["mac_address"] == "AA:BB:CC:DD:EE:01"
    device_id = dev_data["id"]

    # List devices
    res_list = client.get("/api/v1/devices", headers=admin_token_headers)
    assert res_list.status_code == status.HTTP_200_OK
    items = res_list.json()["data"]
    assert any(d["id"] == device_id for d in items)

    # Get single device
    res_single = client.get(f"/api/v1/devices/{device_id}", headers=admin_token_headers)
    assert res_single.status_code == status.HTTP_200_OK
    assert res_single.json()["data"]["id"] == device_id


def test_update_device(client, admin_token_headers):
    # Create device first
    res_create = client.post(
        "/api/v1/devices",
        headers=admin_token_headers,
        json={
            "name": "Smart Lock B",
            "device_type": "smart_lock",
            "mac_address": "11:22:33:44:55:66"
        }
    )
    device_id = res_create.json()["data"]["id"]

    # Update name
    res_update = client.patch(
        f"/api/v1/devices/{device_id}",
        headers=admin_token_headers,
        json={"name": "Smart Lock Entrance B Updated"}
    )
    assert res_update.status_code == status.HTTP_200_OK
    assert res_update.json()["data"]["name"] == "Smart Lock Entrance B Updated"


def test_register_agent_device(client):
    response = client.post(
        "/api/v1/devices/register",
        json={
            "device_id": "PC-LAB-01",
            "hostname": "STUDENT-PC-01",
            "ip": "192.168.1.105",
            "os": "Windows 11 Pro",
            "agent_version": "1.0.0"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert data["data"]["device_id"] == "PC-LAB-01"
    assert data["data"]["hostname"] == "STUDENT-PC-01"
    assert data["data"]["status"] == "online"
    assert "id" in data["data"]

    # Re-register / heartbeat update
    res_update = client.post(
        "/api/v1/devices/register",
        json={
            "device_id": "PC-LAB-01",
            "hostname": "STUDENT-PC-01-RENAMED",
            "ip": "192.168.1.199",
            "os": "Windows 11 Pro",
            "agent_version": "1.0.1"
        }
    )
    assert res_update.status_code == status.HTTP_201_CREATED
    assert res_update.json()["data"]["hostname"] == "STUDENT-PC-01-RENAMED"
    assert res_update.json()["data"]["ip"] == "192.168.1.199"


