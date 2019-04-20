def test_users_me(client, make_token_headers):
    response = client.get("/api/v1/users/me", headers=make_token_headers())
    assert response.status_code == 200
