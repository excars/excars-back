from social_core.backends import google


def save_avatar(backend, user, response, *args, **kwargs):
    del args, kwargs

    avatar = None

    if isinstance(backend, google.GoogleOAuth2):
        image = response.get("image")
        if image:
            avatar = image.get("url")

    if isinstance(backend, google.GooglePlusAuth):
        avatar = response.get("picture")

    if avatar:
        user.avatar = avatar
        user.save()
