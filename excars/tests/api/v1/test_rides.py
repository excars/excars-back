import asyncio

from excars import repositories
from excars.models.profiles import Role
from excars.models.rides import RideRequest


def test_create_ride_request(client, profile_factory, make_token_headers):
    receiver = profile_factory()
    sender = profile_factory(role=Role.opposite(receiver.role))

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, receiver))
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, sender))
        headers = make_token_headers(sender.user_id)
        response = cli.post("/api/v1/rides", headers=headers, json={"receiver": receiver.user_id})

    assert response.status_code == 200
    assert RideRequest(**response.json())


def test_create_ride_request_raises_404(client, faker, make_token_headers):
    with client as cli:
        response = cli.post("/api/v1/rides", headers=make_token_headers(), json={"receiver": faker.pyint()})
    assert response.status_code == 404


def test_create_ride_request_when_sender_is_not_joined(client, profile_factory, make_token_headers):
    receiver = profile_factory()

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, receiver))
        response = cli.post("/api/v1/rides", headers=make_token_headers(), json={"receiver": receiver.user_id})

    assert response.status_code == 200
    assert RideRequest(**response.json())
