import os


def add_path_to_env_var(env_var_name, path_to_add):
    """
    Adds a specified path to the given environment variable.

    :param env_var_name: The name of the environment variable.
    :param path_to_add: The path to append to the environment variable.
    """
    current_value = os.environ.get(env_var_name, '')
    if current_value:
        new_value = f"{path_to_add}{os.pathsep}{current_value}"
    else:
        new_value = path_to_add

    os.environ[env_var_name] = new_value


def setup_plugins_folders_env_variable(caller_file):
    """
    :param caller_file: The __file__ attribute of the calling script.
    """
    root = os.path.realpath(os.path.join(os.path.dirname(caller_file)))

    add_path_to_env_var('PYBLISH_PLUGINS_FOLDERS', os.path.join(root, 'plugins'))
