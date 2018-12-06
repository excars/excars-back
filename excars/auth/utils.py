def extract_user_uid(request) -> str:
    return request.app.auth.extract_payload(request, verify=False)['user_id']
