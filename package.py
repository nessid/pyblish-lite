name = "pyblish_lite"

version = "0.0.0"


description = "Pyblish"

authors = ["nessid", "vbeges", "esoulacroup"]

requires = [
    'pyblish_maya',
]

cachable = False


def commands():
    env.PYTHONPATH.append("{root}")

    env.PYBLISH_PLUGINS_FOLDERS.append('{root}/pyblish_plugins/pyblish_plugins_common/plugins')
    env.PYBLISH_PLUGINS_FOLDERS.append('{root}/pyblish_plugins/pyblish_plugins_maya/plugins')

    # Path to the JSON file listing pyblish plugins active states by asset_types and tasks.
    env.PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON = '{root}/pyblish_plugins_manager/config/pyblish_plugins_settings_by_tasks.json'
    # Path to the JSON file listing production assets types and their associated tasks
    env.PYBLISH_ASSET_TASKS_MAPPING_JSON = '{root}/pyblish_plugins_manager/config/asset_tasks_mapping.json'

    env.MAYA_SCRIPT_PATH.append('{root}/pyblish_lite/pythonpath')
    env.PYTHONPATH.append("{env.MAYA_SCRIPT_PATH}")  # Needed for userSetupy.py to execute

    env.PYBLISH_GUI = "pyblish_lite"
