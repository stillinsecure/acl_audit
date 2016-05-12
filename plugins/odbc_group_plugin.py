import pypyodbc
from group_plugin import GroupPlugin, Group


class ODBCGroupPlugin(GroupPlugin):

    def __init__(self):
        super(ODBCGroupPlugin, self).__init__()
        self.connection_str = self.get_conf_option('connection_str')
        self.groups_sql = self.get_conf_option('groups_sql')
        self.change_group_sql = self.get_conf_option('change_group_sql')

    def get_list(self):
        groups = []

        connection = None
        try:
            connection = pypyodbc.connect(self.connection_str)
            rows = connection.cursor().execute(self.groups_sql)
            for row in rows:
                groups.append(Group(row[0], row[1]))
            return groups
        except pypyodbc.DatabaseError as ex:
            raise
        finally:
            if connection is not None:
                connection.close()

    def change_group(self, user_id, group_id):
        connection = None
        try:
            connection = pypyodbc.connect(self.connection_str)
            connection.cursor().execute(self.change_group_sql, (group_id, user_id))
            connection.commit()
        except:
            raise
        finally:
            if connection is not None:
                connection.close()
