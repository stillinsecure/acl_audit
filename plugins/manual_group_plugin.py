from group_plugin import GroupPlugin, Group


class ManualGroupPlugin(GroupPlugin):

    def __init__(self):
        super(ManualGroupPlugin, self).__init__()

    def get_list(self):
        # Add you groups here, id and name
        return [Group('1', 'Demo')]

    def change_group(self, user_id, group_id):
        group = [g for g in self.get_list() if g.id == group_id][0]
        message = 'Change the group for user {0} to group ({1}):{2}\r\nPress enter \
                   when complete\r\n'.format(user_id, group.name, group.id)
        raw_input(message)