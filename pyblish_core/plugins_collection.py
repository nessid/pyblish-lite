import os
import json
from typing import List, Type
import pyblish.api
from pyblish_core.plugins_data_generator import PluginsDataGenerator
from pyblish_core.lib import configure_logging

# Configure logging
log = configure_logging(__name__)


class PluginsCollect(object):
    """
    A class to collect and manage Pyblish plugins for a specific asset type and task based on JSON configuration files.

    :param plugins: (List[Type[pyblish.api.Plugin]]) List of Pyblish plugin classes.
    """

    def __init__(self, plugins: List[Type[pyblish.api.Plugin]]):
        """
        Initialize the PluginsCollect instance with a list of Pyblish plugin classes.

        :param plugins: A list of Pyblish plugin classes.
        """
        self.plugins = plugins

    @classmethod
    def from_asset_task(cls, asset_type: str, task: str) -> 'PluginsCollect':
        """
        Create a PluginsCollect instance for a specific asset and task from JSON configuration files.

        :param asset_type: (str) The asset type for which plugins are being collected.
        :param task: (str) The specific task for which plugins are being collected.
        :return: (PluginsCollect) An instance of PluginsCollect containing relevant plugins.
        """
        # Retrieve paths for JSON configuration files from environment variables.
        plugins_activation_env_var = 'PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON'
        pyblish_plugins_settings_by_task = os.getenv(plugins_activation_env_var)

        if not pyblish_plugins_settings_by_task:
            log.warning(f"Environment variable '{plugins_activation_env_var}' is not set.")
            # Create an empty JSON file
            with open(pyblish_plugins_settings_by_task, 'w') as file:
                json.dump({}, file)

        # Load or create the JSON file
        if not os.path.exists(pyblish_plugins_settings_by_task):
            log.warning(f"File not found: {pyblish_plugins_settings_by_task}")
            # Create an empty JSON file
            with open(pyblish_plugins_settings_by_task, 'w') as file:
                json.dump({}, file)

        with open(pyblish_plugins_settings_by_task, 'r') as file:
            asset_task_plugins_settings = json.load(file).get(asset_type, {}).get(task, {})

        generator = PluginsDataGenerator()
        plugins_data = generator.collect_plugins_data()

        # Collect plugins based on the configuration for the specified asset type and task.
        plugins = []
        for plugin_id, plugin_settings in asset_task_plugins_settings.items():
            if not plugin_settings['active']:
                continue
            try:
                plugin_class = plugins_data[plugin_id]['plugin_class']
                plugin_class.failure_response = plugin_settings.get('failure_response', 'fail')
                plugins.append(plugin_class)
            except KeyError:
                # Handle the case where plugin_id is not found in plugins_data
                print(f"Error: The key '{plugin_id}' was not found in plugins_data.")
            except Exception as e:
                # Handle any other exceptions
                print(f"An unexpected error occurred: {e}")

        return cls(plugins)
