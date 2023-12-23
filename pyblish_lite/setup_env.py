import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


def add_path_to_env_var(env_var_name, path_to_add):
    """
    Adds a specified path to the given environment variable.

    :param env_var_name: The name of the environment variable.
    :param path_to_add: The path to append to the environment variable.
    """
    current_value = os.environ.get(env_var_name, '')
    if current_value:
        # Append the path with the appropriate separator
        new_value = f"{path_to_add}{os.pathsep}{current_value}"
    else:
        # Set the new value as the path if the env var was not set
        new_value = path_to_add

    os.environ[env_var_name] = new_value


def setup_env_variables():

    log.info('setup_env_variables')

    root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

    add_path_to_env_var('MAYA_SCRIPT_PATH', os.path.join(root, 'pyblish_lite', 'pythonpath'))
    add_path_to_env_var('PYTHONPATH', os.environ['MAYA_SCRIPT_PATH'])  # Needed for userSetupy.py to execute

    add_path_to_env_var('PYTHONPATH', os.path.join(root, 'pyblish_core'))
    add_path_to_env_var('PYTHONPATH', os.path.join(root, 'pyblish_plugins'))
    add_path_to_env_var('PYTHONPATH', os.path.join(root, 'pyblish_plugins_manager'))

    add_path_to_env_var('PYBLISH_PLUGINS_FOLDERS', os.path.join(root, 'pyblish_plugins', 'pyblish_plugins_common',
                                                                'plugins'))
    add_path_to_env_var('PYBLISH_PLUGINS_FOLDERS', os.path.join(root, 'pyblish_plugins', 'pyblish_plugins_maya',
                                                                'plugins'))

    # Path to the JSON file listing pyblish pyblish_plugins active states by asset_types and tasks.
    os.environ['PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON'] = os.path.join(root, 'pyblish_plugins_manager', 'config',
                                                                        'pyblish_plugins_settings_by_tasks.json')
    # Path to the JSON file listing production assets types and their associated tasks
    os.environ['PYBLISH_ASSET_TASKS_MAPPING_JSON'] = os.path.join(root, 'pyblish_plugins_manager', 'config',
                                                                  'asset_tasks_mapping.json')

    os.environ['PYBLISH_GUI'] = 'pyblish_lite'
