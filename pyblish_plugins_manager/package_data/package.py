name = "pyblish_plugins_manager"

version = "0.0.0"


description = "Pyblish plugin manager designed for context-based plugin loading and management."

authors = ["nessid"]

requires = [
            'pyblish_core',
            ]

variants = []

cachable = False

# proprietary variables
_package_origin = "internal"
_package_type = "lib"


def commands():
    env.PYTHONPATH.append("{root}")
