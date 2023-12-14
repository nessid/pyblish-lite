name = "pyblish_core"

version = "0.0.0"


description = "Repository to access all available plugins and load them according context."

authors = ["nessid"]

requires = [
            'engines_software_manager',
            'env_base',
            'pyblish_base',
            ]

variants = []

cachable = False

# proprietary variables
_package_origin = "internal"
_package_type = "lib"


def pre_commands():
    # Path to the JSON file listing pyblish plugins active states by asset_types and tasks.
    env.PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON = "{env.CONFIG_ROOT}/pyblish/pyblish_plugins_settings_by_tasks.json"
    # Path to the JSON file listing production assets types and their associated tasks
    env.PYBLISH_ASSET_TASKS_MAPPING_JSON = "{env.CONFIG_ROOT}/pyblish/asset_tasks_mapping.json"


def commands():
    env.PYTHONPATH.append("{root}")
