import os

root = os.path.dirname(__file__)

os.environ['PYBLISH_PLUGINS_FOLDERS'] += f'{root}/pyblish_plugins/pyblish_plugins_common/plugins'
os.environ['PYBLISH_PLUGINS_FOLDERS'] += f'{root}/pyblish_plugins/pyblish_plugins_maya/plugins'

# Path to the JSON file listing pyblish pyblish_plugins active states by asset_types and tasks.
os.environ['PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON'] = f'{root}/config/pyblish_plugins_settings_by_tasks.json'
# Path to the JSON file listing production assets types and their associated tasks
os.environ['PYBLISH_ASSET_TASKS_MAPPING_JSON'] = f'{root}/config/asset_tasks_mapping.json'

os.environ['MAYA_SCRIPT_PATH'] += f'{root}/pyblish_lite/pythonpath'
os.environ['PYTHONPATH'] += os.environ['MAYA_SCRIPT_PATH']  # Needed for userSetupy.py to execute

os.environ['PYBLISH_GUI'] = 'pyblish_lite'