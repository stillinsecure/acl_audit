from flow_plugin import FlowPlugin
from ghost import Ghost
from netlib.odict import ODict

import Cookie


class ACSFlowPlugin(FlowPlugin):

    fed_auth_cookies = []

    def __init__(self):
        super(ACSFlowPlugin, self).__init__()
        self.url = self.get_conf_option('url')
        self.username = self.get_conf_option('username')
        self.password = self.get_conf_option('password')

    def start_session(self):

        ACSFlowPlugin.fed_auth_cookies = []
        g = Ghost()
        with g.start() as session:
            session.open(self.url)
            session.wait_for_selector('div.windows-live-label.unselectable.tappable')
            session.evaluate('windowsLiveSignin();', expect_loading=True)
            session.wait_for_selector('form[name=f1]')
            session.evaluate("document.querySelector('input[name=loginfmt]').value = '{0}';".format(self.username))
            session.set_field_value('input[name=passwd]', '{0}'.format(self.password))
            page, resources = session.evaluate("document.querySelector('input[type=submit]').click()", expect_loading=True)

            cookie = Cookie.SimpleCookie(str(page.headers['Set-Cookie']).encode('ascii'))
            tmp = ''
            for key in cookie:
                tmp += '{0}={1}; '.format(key, cookie[key].value)

            ACSFlowPlugin.fed_auth_cookies.append(tmp)

    def end_session(self):
        pass

    def remove_session(self, f):
        f.request.cookies = ODict()
        f.request.headers.pop('cookie')

    def request(self, f):
        f.request.headers.set_all('Cookie', ACSFlowPlugin.fed_auth_cookies)
