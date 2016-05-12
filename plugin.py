import imp
import inspect
import ConfigParser

class PluginException(Exception):

    def __init__(self, message=None):
        super(PluginException, self).__init__(message)

class Plugin(object):

    def __init__(self):
        path = 'plugins/plugin.conf'
        self.config = ConfigParser.ConfigParser()
        self.config.read(path)

    @staticmethod
    def load_plugin(name):
        if name is None:
            return None
        sections = name.split(".")
        path = 'plugins/{0}.py'.format(sections[0])
        message = None
        try:
            module = imp.load_source(sections[0], path)
            for cls_name, cls_type in inspect.getmembers(module):
                if cls_name == sections[1]:
                    return cls_type()
            message = 'Could not find the plugin class {0} in module {1}'.format(sections[1], module)
        except IOError as error:
            message = 'An IO error has occurred loading the plugin {0}\r\n{1}'.format(path, error.args)
        except TypeError as error:
            message = 'Could not create an instance of the plugin {0}\r\n{1}'.format(cls_name, error.args)
        raise PluginException(message)

    def get_conf_option(self, option):
        name = type(self).__name__
        module = type(self).__module__
        section = '{0}.{1}'.format(module, name)
        value = self.config.get(section, option)
        return value



