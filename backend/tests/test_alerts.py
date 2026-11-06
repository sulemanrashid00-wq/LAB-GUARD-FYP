from fastapi import status


def test_create_and_manage_alert(client, user_token_headers):
    # Create an alert
    res_create = client.post(
        "/api/v1/alerts",
        headers=user_token_headers,
        json={
            "lab_id": 1,
            "title": "Abnormal Gas Concentration Detected",
            "description": "LPG sensor reported 550 PPM in chemistry fume hood section.",
            "severity": "high"
        }
    )
    assert res_create.status_code == status.HTTP_201_CREATED
    alert = res_create.json()["data"]
    alert_id = alert["id"]
    assert alert["status"] == "active"

    # List active alerts
    res_list = client.get("/api/v1/alerts?status=active", headers=user_token_headers)
    assert res_list.status_code == status.HTTP_200_OK
    assert any(a["id"] == alert_id for a in res_list.json()["data"])

    # Acknowledge the alert
    res_ack = client.patch(
        f"/api/v1/alerts/{alert_id}",
        headers=user_token_headers,
        json={"status": "acknowledged"}
    )
    assert res_ack.status_code == status.HTTP_200_OK
    assert res_ack.json()["data"]["status"] == "acknowledged"

    # Resolve the alert
    res_res = client.patch(
        f"/api/v1/alerts/{alert_id}",
        headers=user_token_headers,
        json={"status": "resolved"}
    )
    assert res_res.status_code == status.HTTP_200_OK
    assert res_res.json()["data"]["status"] == "resolved"

