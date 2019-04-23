import asyncio

from excars import repositories
from excars.models.profiles import Role


def test_ws_receive_empty_map(client, make_token_headers):
    with client as cli, cli.websocket_connect("/api/v1/ws", headers=make_token_headers()) as ws:
        data = ws.receive_json()
        assert data == {"type": "MAP", "data": []}


def test_ws_send_map(client, profile_factory, make_token_headers):
    driver = profile_factory(role=Role.driver)
    hitchhiker = profile_factory(role=Role.opposite(driver.role))

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, driver))
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, hitchhiker))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(driver.user_id)) as ws:
            ws.send_json({"type": "LOCATION", "data": {"longitude": 1, "latitude": 1, "course": -1}})

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(hitchhiker.user_id)) as ws:
            ws.send_json({"type": "LOCATION", "data": {"longitude": 1, "latitude": 1, "course": -1}})

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(hitchhiker.user_id)) as ws:
            data = ws.receive_json()
            map_item = data["data"][0]
            assert map_item["user_id"] == driver.user_id
