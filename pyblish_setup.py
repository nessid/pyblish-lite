import os
from pyblish_core.lib import configure_logging
from pyblish_core.env_lib import add_path_to_env_var


def setup_env_variables():

    log = configure_logging(__name__)

    log.info('setup_env_variables')

    root = os.path.realpath(os.path.join(os.path.dirname(__file__)))

    add_path_to_env_var('PYTHONPATH', os.path.join(root, 'pyblish_core'))
    add_path_to_env_var('PYTHONPATH', os.path.join(root, 'pyblish_plugins'))
    add_path_to_env_var('PYTHONPATH', os.path.join(root, 'pyblish_plugins_manager'))

    # Path to the JSON file listing pyblish pyblish_plugins active states by asset_types and tasks.
    os.environ['PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON'] = os.path.join(root, 'pyblish_plugins_manager', 'config',
                                                                        'pyblish_plugins_settings_by_tasks.json')
    # Path to the JSON file listing production assets types and their associated tasks
    os.environ['PYBLISH_ASSET_TASKS_MAPPING_JSON'] = os.path.join(root, 'pyblish_plugins_manager', 'config',
                                                                  'asset_tasks_mapping.json')

    os.environ['PYBLISH_GUI'] = 'pyblish_lite'

    # Initialize asset_type and task
    os.environ['PYBLISH_LITE_ASSET_TYPE'] = ''
    os.environ['PYBLISH_LITE_TASK'] = ''


def import_modules():
    # Attempt to import Pyblish modules
    # This is where the actual Pyblish functionality is imported into the script
    try:
        # import pyblish_lite
        import pyblish
        import pyblish_core
        import pyblish_plugins_manager
    except ImportError as e:
        # In case of import errors, print the traceback
        # This helps in diagnosing what went wrong during the import process
        import traceback
        print("Pyblish Lite: Could not load integration: %s" % traceback.format_exc())


setup_env_variables()
import_modules()


def run_pyblish_maya_setup(pyblish_maya_path):
    import runpy

    # Construct the full path to the userSetup.py file in the Pyblish Maya package
    # This is done by joining the base path with the relative path to the file
    user_setup_path = os.path.join(pyblish_maya_path, 'pyblish_maya', 'pythonpath', 'userSetup.py')

    # Run the userSetup.py script (to run pyblish_maya.setup() that adds pyblish in the Maya 'File' menu)
    # This executes the script as if it was a standalone Python script
    runpy.run_path(user_setup_path)
