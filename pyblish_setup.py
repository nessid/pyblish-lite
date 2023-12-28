import os
from pyblish_core.lib import configure_logging

# Configure logging for this module
log = configure_logging(__name__)


def setup_env_variables():
    """
    Set up environment variables for the Pyblish application.
    """
    from pyblish_core.env_lib import add_path_to_env_var

    log.info('Setting up Pyblish Lite environment variables')

    root = os.path.dirname(os.path.realpath(__file__))

    # Adding necessary paths to PYTHONPATH
    for sub_dir in ['pyblish_core', 'pyblish_plugins', 'pyblish_plugins_manager']:
        add_path_to_env_var('PYTHONPATH', os.path.join(root, sub_dir))

    # Setting environment variables for Pyblish configuration
    os.environ['PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON'] = os.path.join(root, 'pyblish_plugins_manager', 'config',
                                                                        'pyblish_plugins_settings_by_tasks.json')
    os.environ['PYBLISH_ASSET_TASKS_MAPPING_JSON'] = os.path.join(root, 'pyblish_plugins_manager', 'config',
                                                                  'asset_tasks_mapping.json')
    os.environ['PYBLISH_GUI'] = 'pyblish_lite'
    os.environ['PYBLISH_LITE_ASSET_TYPE'] = ''
    os.environ['PYBLISH_LITE_TASK'] = ''


def initialize_pyblish_lite():
    """
    Initialize Pyblish Lite environment and configurations.
    """
    import pyblish.api
    from pyblish_core.tokens_updater import TokensUpdater

    setup_env_variables()

    # Instantiate TokensUpdater and register callback
    tokens_updater = TokensUpdater()
    log.info('Instantiated TokensUpdater')

    def on_pyblish_lite_reset():
        """
        Callback function for Pyblish Lite reset event.
        """
        asset_type = os.getenv('PYBLISH_LITE_ASSET_TYPE')
        task = os.getenv('PYBLISH_LITE_TASK')
        tokens_updater.register_plugins_by_task(asset_type, task)
        log.info(f'Pyblish Lite reset: Asset Type: {asset_type}, Task: {task}')

    pyblish.api.register_callback("pyblish_lite_reset", on_pyblish_lite_reset)


def run_pyblish_maya_setup(pyblish_maya_path: str):
    """
    Execute the Pyblish Maya setup script.

    :param pyblish_maya_path: Path to the Pyblish Maya directory.
    :type pyblish_maya_path: str
    """
    import runpy

    log.info('Run Pyblish Maya userSetup.py')
    user_setup_path = os.path.join(pyblish_maya_path, 'pyblish_maya', 'pythonpath', 'userSetup.py')
    runpy.run_path(user_setup_path)
