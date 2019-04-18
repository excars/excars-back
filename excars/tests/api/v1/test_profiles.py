import asyncio

from excars import repositories
from excars.models.profiles import Profile


def test_join(client, token_headers):
    with client as cli:
        response = cli.post(
            "/api/v1/profiles",
            headers=token_headers,
            json={"role": "driver", "destination": {"name": "Porto Bello", "latitude": 0, "longitude": 0}},
        )

    assert response.status_code == 200
    assert response.json()["role"] == "driver"


def test_get_profile(client, faker, token_headers):
    profile = Profile(user_id=faker.pyint(), name=faker.pystr(), avatar=faker.pystr())

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile))
        response = cli.get(f"/api/v1/profiles/{profile.user_id}", headers=token_headers)

    assert response.status_code == 200
    assert Profile(**response.json()) == profile


def test_get_profile_returns_404(client, faker, token_headers):
    with client as cli:
        response = cli.get(f"/api/v1/profiles/{faker.pyint()}", headers=token_headers)

    assert response.status_code == 404
