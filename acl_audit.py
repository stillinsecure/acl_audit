import configargparse
from auditing import AuditManager

parser = configargparse.ArgParser(default_config_files=['acl_audit.conf'])

parser.add_argument('--userid', help='The identifier of the user')
parser.add_argument('--mode', help='Specify the mode for acl_audit', choices=['record', 'audit'], default='record')
parser.add_argument('--replay_file', help='File to use for recording or auditing')
parser.add_argument('--flow', help='Name of the flow plugin module to use')
parser.add_argument('--group', help='Name of the group plugin to use. Format = modulename.classname')
parser.add_argument('--path_filter', help='Regex to filter request path on')
parser.add_argument('--domains', help='Domains used for sticky cookies', action='append')
parser.add_argument('--null_session', help='If true then a null session will be used only', choices=[True, False], default=False, type=bool)
parser.add_argument('--ignore', help='Regex of path extensions to ignore', default='js|png|css|less|properties|html|ico')

options = parser.parse_args()

if options.mode == 'audit':
    if not options.null_session and options.group is None:
        parser.error('A group plugin must be specified when nullsession is False')
    if options.group is not None and options.userid is None:
        parser.error('A user id must be specified when using a group plugin')

try:
    mgr = AuditManager(options)
    if options.mode == 'record':
        mgr.record()
    elif options.mode == 'audit':
        results = mgr.audit()
        mgr.compare(results)
except KeyboardInterrupt:
    exit()
except Exception as ex:
    print ex.args