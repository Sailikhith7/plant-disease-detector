import requests

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    response = requests.get(f"{BASE_URL}/health")

    print("\n--- HEALTH TEST ---")
    print("Status:", response.status_code)
    print("Response:", response.json())

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_farmers():
    response = requests.get(f"{BASE_URL}/api/farmers/")

    print("\n--- FARMERS TEST ---")
    print("Status:", response.status_code)
    print("Number of farmers:", len(response.json()))

    assert response.status_code == 200
    assert len(response.json()) == 22


def test_alert_thresholds():
    response = requests.get(
        f"{BASE_URL}/api/alerts/outbreaks",
        params={"threshold": 5}
    )

    print("\n--- ALERT THRESHOLD TEST ---")
    print("Status:", response.status_code)
    print("Response:", response.json())

    assert response.status_code == 200


def test_broadcast():
    payload = {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "custom_message": "This is a demo outbreak advisory."
    }

    response = requests.post(
        f"{BASE_URL}/api/alerts/broadcast",
        json=payload
    )

    print("\n--- BROADCAST TEST ---")
    print("Status:", response.status_code)
    print("Response:", response.json())

    assert response.status_code == 200


if __name__ == "__main__":
    test_health()
    test_farmers()
    test_alert_thresholds()
    test_broadcast()

    print("\n================================")
    print("ALL BASIC PIPELINE TESTS PASSED")
    print("================================")