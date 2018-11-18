import urllib.parse

from sanic import response
from social_core.backends import google
from social_core.strategy import BaseStrategy
from social_flask_peewee.models import FlaskStorage


def load_strategy(request):
    return SanicStrategy(FlaskStorage, request=request)


def load_backend(strategy, redirect_uri=''):
    if 'id_token' in strategy.request_data():
        return google.GooglePlusAuth(strategy, redirect_uri)
    return google.GoogleOAuth2(strategy, redirect_uri)


class SanicStrategy(BaseStrategy):  # pylint: disable=too-many-public-methods

    def __init__(self, storage, request, tpl=None):
        self.request = request
        super().__init__(storage, tpl)

    def get_setting(self, name):
        return getattr(self.request.app.config, name)

    def request_data(self, merge=True):
        data = self.request.get('auth_data', {})
        return data

    def request_post(self):
        return self.request.form.copy()

    def request_get(self):
        return self.request.args.copy()

    def request_host(self):
        return self.request.host.partition(':')[0]

    def request_port(self):
        return self.request.host.partition(':')[2]

    def request_path(self):
        return self.request.path

    def request_is_secure(self):
        return self.request.scheme == 'https'

    def build_absolute_uri(self, path=None):
        url = f'{self.request.scheme}://{self.request.host}'
        if path:
            return urllib.parse.urljoin(url, path)
        return f'{url}{self.request.path}'

    def redirect(self, url):
        return response.redirect(url)

    def html(self, content):
        return response.html(content)

    def session_get(self, name, default=None):
        pass

    def session_set(self, name, value):
        pass

    def session_pop(self, name):
        pass
