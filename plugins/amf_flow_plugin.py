from pyamf import remoting
from pyamf.flex.messaging import RemotingMessage, AcknowledgeMessage, ErrorMessage
from flow_plugin import FlowPlugin


class AMFFlowPlugin(FlowPlugin):

    def __init__(self):
        super(AMFFlowPlugin, self).__init__()
        self.messages = []

    def response(self, flow):
        self.messages = []
        if 'content-type' in flow.request.headers and \
                        flow.request.headers['content-type'] == 'application/x-amf':
            content = flow.request.content
            envelope = remoting.decode(content, strict=False)
            for request in envelope.items():
                request = request[1]
                if type(request.body) is list:
                    for message in request.body:
                        if type(message) is RemotingMessage or type(message) is ErrorMessage:
                            self.messages.append(message)
            if len(self.messages) > 0:
                return True
        return False

    def format_request(self, flow):
        request = ''
        for message in self.messages:
            request += '{0}.{1}\r\n'.format(message.source, message.operation)
        return request

    def format_result(self, result, group):
        fmt_result = ''
        envelope = remoting.decode(result.response, strict=False)
        for response in envelope.items():
            response = response[1]
            if type(response.body) is AcknowledgeMessage:
                message = response.body
                fmt_result += '{0} - {1}\r\n'.format(group, message.body)
            elif type(response.body) is ErrorMessage:
                message = response.body.faultString
                fmt_result += '{0} - {1}\r\n'.format(group, message)
        return fmt_result