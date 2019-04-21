def test_ws_receive_map(client, make_token_headers):
    with client as cli, cli.websocket_connect("/api/v1/ws", headers=make_token_headers()) as ws:
        ws.send_json({})
        data = ws.receive_json()
        assert data == {"type": "MAP", "data": []}
