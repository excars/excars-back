from sanic import response
from social_core import strategy


# pylint: disable=too-many-public-methods
class SanicStrategy(strategy.BaseStrategy):

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
        return self.request.host

    def request_port(self):
        return self.request.port

    def request_path(self):
        return self.request.path

    def request_is_secure(self):
        return self.request.scheme == 'https'

    def build_absolute_uri(self, path=None):
        return 'http://localhost:3000'

    def redirect(self, url):
        return response.redirect(url)

    def html(self, content):
        return response.html(content)

    def session_pop(self, name):
        pass

    def session_set(self, name, value):
        pass

    def session_get(self, name, default=None):
        pass
