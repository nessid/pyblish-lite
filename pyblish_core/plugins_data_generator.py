import os
import json
import inspect
import importlib
import pyblish.api
from typing import List, Dict, Optional, Tuple


class PluginsDataGenerator:
    """Class for generating a JSON file with plugin information."""

    def collect_plugins_data(self, include_class: bool = True) -> Dict:
        """Collect plugins data from all plugin files in specified folders.

        Args:
        :param include_class: (bool) If True, include 'plugin_class' in the data.

        :return Dict: Dictionary of collected plugins' data.
        """
        plugins_folder_env_var_list = os.getenv('PYBLISH_PLUGINS_FOLDERS', '')
        # Splitting the string by ':' to get a list of paths
        plugins_folders = plugins_folder_env_var_list.split(':')

        plugins_data = {}
        for plugins_folder in plugins_folders:
            for plugins_file in self._list_python_files(plugins_folder):
                module_path = PluginsDataGenerator._convert_filepath_to_module_path(plugins_file)
                module_plugins = self._get_pyblish_plugins(module_path)
                for plugin_class in module_plugins:
                    # Create a dictionary for each plugin
                    plugin_data = {
                        "plugin_filepath": plugins_file,
                        "module_path": module_path,
                        "plugin_category": plugin_class.category,
                        "plugin_label": plugin_class.label,
                        "plugin_doc": plugin_class.__doc__,
                        "mandatory": plugin_class.mandatory
                    }

                    # Add 'plugin_class' to plugin data if 'include_class' argument is true
                    # Useful for creating a JSON representation, as classes cannot be serialized
                    if include_class:
                        plugin_data["plugin_class"] = plugin_class

                    # Add the plugin information to the main dictionary
                    plugins_data[plugin_class.plugin_id] = plugin_data

        return plugins_data

    def dump_json_file(self, file_path: str, data: Dict):
        """Create a JSON file with provided data."""
        with open(file_path, 'w+') as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def _list_python_files(folder_path: str) -> List[str]:
        """List Python files in a folder, excluding '__init__.py'."""
        return [os.path.join(root, file)
                for root, _, files in os.walk(folder_path)
                for file in sorted(files) if file.endswith(".py") and file != "__init__.py"]

    @staticmethod
    def _get_pyblish_plugins(module_path: str) -> Optional[Tuple[str, List[Dict]]]:
        """Extract Pyblish plugin data from a module filepath."""
        module = importlib.import_module(module_path)


        module_plugins = []
        for name in dir(module):
            obj = getattr(module, name)
            if PluginsDataGenerator._is_pyblish_plugin(obj):
                module_plugins.append(obj)

        return module_plugins

    @staticmethod
    def _convert_filepath_to_module_path(filepath: str) -> str:
        """Convert a file path to a Python module path."""
        module_parts = filepath.replace('.py', '').replace('/', '.').replace('\\', '.').split('.')
        module_path = '.'.join(module_parts[-5:])
        return module_path

    @staticmethod
    def _is_pyblish_plugin(obj) -> bool:
        """Check if an object is a Pyblish plugin class."""
        return inspect.isclass(obj) and issubclass(obj, pyblish.api.Plugin)


if __name__ == '__main__':
    pass
