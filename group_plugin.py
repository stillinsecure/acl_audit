from plugin import Plugin


class Group(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name


class GroupPlugin(Plugin):

    def __init__(self):
        super(GroupPlugin, self).__init__()

    def get_list(self):
        """
        Returns a list of groups that will be tested
        """
        pass

    def change_group(self, user_id, group_id):
        """
        Changes the group that the user belongs to
        """
        pass


