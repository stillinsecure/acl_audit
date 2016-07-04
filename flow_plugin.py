import re
from netlib.odict import ODict

from plugin import Plugin


class FlowResult(object):

    def __init__(self,
                 flow_id,
                 report_col_name,    # This is a generated name that is used by the report to group results
                 path,
                 status_code,
                 response,
                 content_type):
        self.flow_id = flow_id
        self.path = path
        self.status_code = status_code
        self.response = response
        self.content_type = content_type
        self.report_col_name = report_col_name

class FlowPlugin(Plugin):

    def __init__(self):
        super(FlowPlugin, self).__init__()
        self.current_flow_id = 0

    def request(self, flow):
        pass

    def response(self, flow):
        return True

    def format_result(self, flow_result, group):
        response = re.sub('[\r,\n,\t]', '', flow_result.response)
        return 'Status Code:{0:4} {1}'.format(flow_result.status_code, response)

    def remove_session(self, flow):
        flow.request.cookies = ODict()
        flow.request.headers.pop('cookie')

    def format_request(self, request):
        return request.path

    def start_session(self):
        pass

    def end_session(self):
        pass
