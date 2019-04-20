import asyncio
import random

from excars import repositories
from excars.models.profiles import Profile, Role


def test_join(client, faker, make_token_headers):
    role = random.choice([Role.driver, Role.hitchhiker])
    with client as cli:
        response = cli.post(
            "/api/v1/profiles",
            headers=make_token_headers(),
            json={
                "role": role,
                "destination": {
                    "name": faker.name(),
                    "latitude": str(faker.latitude()),
                    "longitude": str(faker.longitude()),
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["role"] == role


def test_get_profile(client, profile_factory, make_token_headers):
    profile = profile_factory()

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile))
        response = cli.get(f"/api/v1/profiles/{profile.user_id}", headers=make_token_headers())

    assert response.status_code == 200
    assert Profile(**response.json()) == profile


def test_get_profile_returns_404(client, faker, make_token_headers):
    with client as cli:
        response = cli.get(f"/api/v1/profiles/{faker.pyint()}", headers=make_token_headers())
    assert response.status_code == 404
