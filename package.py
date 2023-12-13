name = 'pyblish_lite'

version = '1.1.0'

description = 'The pyblish-lite repository with nessid custom code. Started from openpipe archived pyblish-lite repo ' \
              'https://github.com/ynput/pyblish-lite'

authors = ['vbeges', 'esoulacroup', 'nessid']

requires = [
            'pyblish_base',
            'pyblish_core',
            ]


def commands():
    env.PYTHONPATH.append('{root}/python')
    env.PYBLISH_GUI = "pyblish_lite"
    env.MAYA_SCRIPT_PATH.append('{root}/python/pyblish_lite/pythonpath')
