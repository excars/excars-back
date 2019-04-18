from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starlette.testclient import TestClient


def test_join(client: "TestClient", token_headers):
    response = client.post(
        "/api/v1/join",
        headers=token_headers,
        json={"role": "driver", "destination": {"name": "Porto Bello", "latitude": 0, "longitude": 0}},
    )
    assert response.status_code == 200

    content = response.json()
    assert content["role"] == "driver"
