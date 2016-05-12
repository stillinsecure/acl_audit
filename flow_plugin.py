import re

from plugin import Plugin


class FlowResult(object):

    def __init__(self,
                 flow_id,
                 group_id,
                 path,
                 status_code,
                 response):
        self.flow_id = flow_id
        self.path = path
        self.status_code = status_code
        self.response = response
        self.group_id = group_id
        self.null_session = self.group_id is None


class FlowPlugin(Plugin):

    def __init__(self):
        super(FlowPlugin, self).__init__()

    def request(self, flow):
        pass

    def response(self, flow):
        return True

    def format_result(self, flow_result, group):
        response = re.sub('[\r,\n,\t]', '', flow_result.response)
        return 'Status Code:{0:4} {1}'.format(flow_result.status_code, response)

    def format_request(self, request):
        return request.path

    def start_session(self):
        pass

    def end_session(self):
        pass
