from pyblish_core.plugins_collection import PluginsCollect
from pyblish.api import (
    register_plugin,
    deregister_all_paths,
    deregister_all_plugins
    )


class PluginsRegister(object):
    """
    This class is responsible for registering plugins from a PluginsCollect.

    It iterates through the collection's plugins and registers each one using
    the register_plugin function from Pyblish.
    """
    def __init__(self, plugins_collection: PluginsCollect):
        """
        Initialize a new PluginsRegister instance.

        :param plugins_collection: An instance of the PluginsCollect containing the plugins to be registered.
        """
        self.plugins_collection = plugins_collection

    def register(self):
        """
        Register the plugins from the PluginsCollect.

        This method iterates through the plugins in the collection and
        registers each one using the register_plugin function from Pyblish.
        """
        for plugin in self.plugins_collection.plugins:
            register_plugin(plugin)
