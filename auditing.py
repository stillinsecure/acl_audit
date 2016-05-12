from netlib import odict
from mitmproxy import dump, flow, controller, proxy
from flow_plugin import FlowResult, FlowPlugin
from group_plugin import Group
from plugin import Plugin
import os
import re
import xlsxwriter


class RecordMaster(controller.Master):

    def __init__(self, domains, replay_file, path_filter, ignore):
        self.domains = domains
        replay_file = 'output/{0}'.format(replay_file)
        self.tmp_file = open(replay_file, 'wb')
        self.writer = flow.FlowWriter(self.tmp_file)
        self.path_filter = path_filter
        self.ignore = ignore

        config = proxy.ProxyConfig(port=int(8080), http2=False)
        server = proxy.ProxyServer(config)
        super(RecordMaster, self).__init__(server)

    def handle_response(self, f):
        if f.request.host in self.domains:
            if 'strict-transport-security' in f.response.headers:
                f.response.headers['strict-transport-security'] = 'max-age=0;'
            self.filter(f)
        f.reply()

    def filter(self, f):
        if not re.search(self.ignore, f.request.path) and \
               re.search(self.path_filter, f.request.path):
            print '\tRecording {0}'.format(f.request.path)
            self.writer.add(f)


class AuditMaster(dump.DumpMaster):

    def __init__(self,
                 group_plugin,
                 flow_plugin,
                 group_id,
                 domains,
                 replay_file):
        config = proxy.ProxyConfig(port=int(8080), http2=False)
        server = proxy.DummyServer(config)
        opts = dump.Options()
        opts.anticache = True
        opts.flow_detail = 0
        replay_file = 'output/{0}'.format(replay_file)
        opts.client_replay = [replay_file]
        super(AuditMaster, self).__init__(server, opts)

        self.domains = domains
        self.results = []
        self.group_plugin = group_plugin
        self.flow_plugin = flow_plugin
        self.group_id = group_id
        self.current_flow_id = 0
        self.cookies = {}

    def run(self):
        self.flow_plugin.start_session()
        super(AuditMaster, self).run()

    def handle_request(self, f):
        print '\tReplaying {0}'.format(f.request.path)
        if 'cookie' in f.request.headers:
            f.request.cookies = odict.ODict()
            f.request.headers.pop('cookie')
        if self.group_id is not None:
            if f.request.host in self.domains:
                hid = (f.request.host, f.request.port)
                if hid in self.cookies:
                    f.request.headers.set_all('Cookie', self.cookies[hid])
        self.flow_plugin.request(f)
        if self.group_id is None:
            self.flow_plugin.remove_session(f)
        super(AuditMaster, self).handle_request(f)

    def handle_response(self, f):
        if self.group_id is not None:
            if f.request.host in self.domains:
                hid = (f.request.host, f.request.port)
                if 'set-cookie' in f.response.headers:
                    self.cookies[hid] = f.response.headers.get_all('set-cookie')
        if self.flow_plugin.response(f):
            requests = self.flow_plugin.format_request(f.request)
            result = FlowResult(self.current_flow_id,
                                self.group_id,
                                requests,
                                f.response.status_code,
                                f.response.get_decoded_content())
            self.current_flow_id += 1
            self.results.append(result)
        super(AuditMaster, self).handle_response(f)


class AuditManager(object):

        def __init__(self, options):
            self.options = options
            self.results = []
            self.group_plugin = Plugin.load_plugin(options.group)
            self.flow_plugin = Plugin.load_plugin(options.flow)
            if self.flow_plugin is None:
                self.flow_plugin = FlowPlugin()

        def record(self):
            m = RecordMaster(self.options.domains, self.options.replay_file,
                             self.options.path_filter, self.options.ignore)

            try:
                print 'Starting to record flows'
                m.run()
            except Exception as ex:
                print 'Unexpected error has occurred: ', ex.args
            finally:
                m.shutdown()

        def audit(self):
            groups = []

            if not self.options.null_session:
                groups = self.group_plugin.get_list()

            # The None group is used for empty sessions.
            groups.append(None)
            results = []

            for user_group in groups:
                user_group_id = None
                print '\r\n--------------------------------------------------------------------------'
                if user_group is None:
                    print '\r\n Auditing null session'
                else:
                    print ' Auditing group {0}'.format(user_group.name)
                    user_group_id = user_group.id
                    self.group_plugin.change_group(self.options.userid, user_group.id)
                print '\r\n--------------------------------------------------------------------------'

                m = AuditMaster(self.group_plugin,
                                self.flow_plugin,
                                user_group_id,
                                self.options.domains,
                                self.options.replay_file)
                try:
                    m.run()
                except Exception as ex:
                    print 'Unexpected error has occurred: ', ex.args
                    continue
                finally:
                    results.extend(m.results)
                    m.shutdown()

            return results

        def compare(self, results):

            if results is None:
                print 'Nothing found to compare'
                return

            if not self.options.null_session:
                groups = self.group_plugin.get_list()
            else:
                groups = []
            groups.append(Group(0, 'Null Session'))

            workbook_name = 'output/{0}.xlsx'.format(self.options.replay_file)
            workbook = xlsxwriter.Workbook(workbook_name)
            worksheet = workbook.add_worksheet()

            hdr_fmt = workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_name':'Arial'})
            row_fmt = workbook.add_format({'valign': 'top', 'text_wrap' : '1', 'font_name':'Arial', 'font_size':'9'})

            worksheet.set_row(0, 45, hdr_fmt)
            worksheet.set_column('A:Z', 50)
            worksheet.write(0, 0, 'Recorded Request')

            row = 0
            col = 1

            for group in groups:
                worksheet.write(row, col, group.name)
                col += 1

            unique_flows = {}

            for result in results:

                if result.flow_id in unique_flows:
                    continue

                unique_flows[result.flow_id] = result.flow_id

                col = 0
                row += 1
                worksheet.set_row(row, 30, row_fmt)

                match_results = [f for f in results if f.flow_id == result.flow_id]
                worksheet.write(row, col, result.path)

                for match_result in match_results:
                    col += 1
                    if match_result.null_session:
                        group_name = 'Null Session'
                    else:
                        group = [g for g in groups if g.id == match_result.group_id]
                        group_name = group[0].name
                    try:
                        result_t = self.flow_plugin.format_result(match_result, group_name)
                        if result_t is not None:
                            worksheet.write(row, col, result_t)
                    except Exception as ex:
                        print 'Unexpected error formatting result: ', ex.args
                        continue

                os.system('clear')
            workbook.close()