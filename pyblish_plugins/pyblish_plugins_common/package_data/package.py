name = 'pyblish_plugins_common'

version = '0.3.0'

description = 'Pyblish commons plugins used in any software'

authors = ['vbeges', 'nessid']

requires = [
            'engines_software_manager',
            'pyblish_core',
            ]

cachable = True


def commands():
    env.PYTHONPATH.append('{root}')
    env.PYBLISH_PLUGINS_FOLDERS.append('{root}/pyblish_plugins_common/plugins')

    # IMPORTANT : Comment this command for deploy
    # env.PYBLISHPLUGINPATH.append('{root}/pyblish_plugins_common/test_plugins')
