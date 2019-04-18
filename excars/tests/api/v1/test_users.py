def test_users_me(client, token_headers):
    response = client.get("/api/v1/users/me", headers=token_headers)
    assert response.status_code == 200
