import os
from pyblish_core.logging import configure_logging
from pyblish_core.environment_utils import add_path_to_env_var

log = configure_logging(__file__)


def setup_plugins_folders_env_variable(caller_file):
    """
    :param caller_file: The __file__ attribute of the calling script.
    """
    root = os.path.realpath(os.path.join(os.path.dirname(caller_file)))
    plugins_path = os.path.join(root, 'plugins')

    add_path_to_env_var('PYBLISH_PLUGINS_FOLDERS', plugins_path)

    log.info(f'{os.path.basename(os.path.dirname(os.path.realpath(caller_file)))} added to PYBLISH_PLUGINS_FOLDERS')
