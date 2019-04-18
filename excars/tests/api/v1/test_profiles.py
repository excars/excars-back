def test_join(client, token_headers):
    with client as cli:
        response = cli.post(
            "/api/v1/profiles",
            headers=token_headers,
            json={"role": "driver", "destination": {"name": "Porto Bello", "latitude": 0, "longitude": 0}},
        )

    assert response.status_code == 200

    content = response.json()
    assert content["role"] == "driver"
