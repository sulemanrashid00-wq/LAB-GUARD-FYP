from fastapi import status


def test_issue_and_track_device_command(client, user_token_headers, admin_token_headers):
    # Create test device
    dev_res = client.post(
        "/api/v1/devices",
        headers=admin_token_headers,
        json={
            "name": "Smart Door Actuator",
            "device_type": "smart_lock",
            "mac_address": "CC:DD:EE:FF:00:11"
        }
    )
    device_id = dev_res.json()["data"]["id"]

    # Issue command
    res_cmd = client.post(
        "/api/v1/commands",
        headers=user_token_headers,
        json={
            "device_id": device_id,
            "command_type": "lock_door",
            "payload_json": {"auto_relock_seconds": 60}
        }
    )
    assert res_cmd.status_code == status.HTTP_201_CREATED
    cmd = res_cmd.json()["data"]
    cmd_id = cmd["id"]
    assert cmd["status"] == "pending"

    # Query device commands
    res_list = client.get(f"/api/v1/commands/device/{device_id}", headers=user_token_headers)
    assert res_list.status_code == status.HTTP_200_OK
    assert any(c["id"] == cmd_id for c in res_list.json()["data"])

    # Update command execution status
    res_status = client.patch(
        f"/api/v1/commands/{cmd_id}/status",
        headers=user_token_headers,
        json={
            "status": "executed",
            "response_json": {"result": "door successfully locked"}
        }
    )
    assert res_status.status_code == status.HTTP_200_OK
    assert res_status.json()["data"]["status"] == "executed"

