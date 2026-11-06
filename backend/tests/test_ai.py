from fastapi import status


def test_ai_inference_and_analytics(client, user_token_headers):
    # 1. Test normal telemetry inference
    res_normal = client.post(
        "/api/v1/ai/inference",
        headers=user_token_headers,
        json={
            "lab_id": 1,
            "inference_type": "anomaly_detection",
            "current_telemetry": {
                "temperature": 23.0,
                "humidity": 45.0,
                "gas_ppm": 80.0,
                "smoke_detected": False,
                "flame_detected": False
            }
        }
    )
    assert res_normal.status_code == status.HTTP_200_OK
    normal_data = res_normal.json()["data"]
    assert normal_data["is_anomaly"] is False
    assert normal_data["risk_level"] == "low"

    # 2. Test critical hazard condition
    res_hazard = client.post(
        "/api/v1/ai/inference",
        headers=user_token_headers,
        json={
            "lab_id": 1,
            "inference_type": "anomaly_detection",
            "current_telemetry": {
                "temperature": 68.0,
                "humidity": 20.0,
                "gas_ppm": 950.0,
                "smoke_detected": True,
                "flame_detected": True
            }
        }
    )
    assert res_hazard.status_code == status.HTTP_200_OK
    hazard_data = res_hazard.json()["data"]
    assert hazard_data["is_anomaly"] is True
    assert hazard_data["risk_level"] in ["high", "critical"]

    # 3. Test list registered models
    res_models = client.get("/api/v1/ai/models", headers=user_token_headers)
    assert res_models.status_code == status.HTTP_200_OK
    assert len(res_models.json()["data"]) >= 1

    # 4. Test anomaly report
    res_report = client.get("/api/v1/ai/anomalies", headers=user_token_headers)
    assert res_report.status_code == status.HTTP_200_OK
    report_data = res_report.json()["data"]
    assert "total_samples_analyzed" in report_data
    assert "anomalies_detected" in report_data

