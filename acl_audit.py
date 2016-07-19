import configargparse
from auditing import AuditManager, AuditMaster

parser = configargparse.ArgParser(default_config_files=['acl_audit.conf'])

parser.add_argument('--listen_port', help='Port that the proxy server will listen on when mode is set to record', default=8080)
parser.add_argument('--show_ignored', help='Indicates if ignored requests are displayed', default=False)
parser.add_argument('--userid', help='The identifier of the user')
parser.add_argument('--mode', help='Specify the mode for acl_audit', choices=['record', 'audit'], default='record')
parser.add_argument('--replay_file', help='File to use for recording or auditing', default='output')
parser.add_argument('--flow', help='Name of the flow plugin module to use')
parser.add_argument('--group', help='Name of the group plugin to use. Format = modulename.classname')
parser.add_argument('--record_uri_filter', help='Regex to filter request uri on', default='.*')
parser.add_argument('--host', help='Domains used for sticky cookies', default='.*')
parser.add_argument('--record_content_type', help='Regex of path extensions to ignore', default='js|png|css|less|properties|html|ico')
parser.add_argument('--cookie_mode', help='Specifies how the cookies will be created and used', choices=[AuditMaster.RecordedCookieMode,
                                                                                                         AuditMaster.RemoveAllCookieMode,
                                                                                                         AuditMaster.ManualCookieMode])
options = parser.parse_args()

try:
    mgr = AuditManager(options)
    if options.mode == 'record':
        mgr.record()
    elif options.mode == 'audit':
        results = mgr.audit()
        mgr.report(results)
except KeyboardInterrupt:
    exit()
except Exception as ex:
    print ex.args