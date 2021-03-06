def test_users_me(client, make_token_headers):
    with client as cli:
        response = cli.get("/api/v1/users/me", headers=make_token_headers())
    assert response.status_code == 200
