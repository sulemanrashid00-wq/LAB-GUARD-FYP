from fastapi import status


def test_policy_crud_and_enforcement(client, admin_token_headers):
    # Create safety policy
    res_create = client.post(
        "/api/v1/policies",
        headers=admin_token_headers,
        json={
            "lab_id": 1,
            "name": "High Temperature Warning Policy",
            "description": "Trigger alert when temperature exceeds 45 degrees Celsius",
            "rule_type": "temperature_limit",
            "condition_operator": ">",
            "threshold_value": 45.0,
            "action_type": "raise_alert",
            "is_active": True
        }
    )
    assert res_create.status_code == status.HTTP_201_CREATED
    policy = res_create.json()["data"]
    policy_id = policy["id"]
    assert policy["threshold_value"] == 45.0

    # List policies
    res_list = client.get("/api/v1/policies?lab_id=1", headers=admin_token_headers)
    assert res_list.status_code == status.HTTP_200_OK
    assert any(p["id"] == policy_id for p in res_list.json()["data"])

    # Update policy
    res_update = client.patch(
        f"/api/v1/policies/{policy_id}",
        headers=admin_token_headers,
        json={"threshold_value": 50.0}
    )
    assert res_update.status_code == status.HTTP_200_OK
    assert res_update.json()["data"]["threshold_value"] == 50.0

    # Delete policy
    res_del = client.delete(f"/api/v1/policies/{policy_id}", headers=admin_token_headers)
    assert res_del.status_code == status.HTTP_200_OK

