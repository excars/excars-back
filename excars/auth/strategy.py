from sanic import response
from social_core import strategy


class SanicStrategy(strategy.BaseStrategy):

    def __init__(self, storage=None, request=None, tpl=None):
        self.request = request
        super().__init__(storage, tpl)

    def get_setting(self, name):
        return getattr(self.request.app.config, name)

    def request_data(self, merge=True):
        if self.request:
            data = self.request.get('auth_data', {})
            return data
        else:
            return {}

    def request_host(self):
        if self.request:
            return self.request.host

    def build_absolute_uri(self, path=None):
        return 'http://localhost:3000'

    def redirect(self, url):
        return response.redirect(url)

    def html(self, content):
        return response.html(content)
