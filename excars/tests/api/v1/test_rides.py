import asyncio

from excars import repositories
from excars.models.profiles import Role
from excars.models.rides import RideRequest


def test_create_ride_request(client, profile_factory, token_headers):
    receiver = profile_factory(role=Role.driver)
    sender = profile_factory(role=Role.hitchhiker)

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, receiver))
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, sender))

        response = cli.post("/api/v1/rides", headers=token_headers, json={"receiver": receiver.user_id})

    print(response.content)
    assert response.status_code == 200
    assert RideRequest(**response.json())
