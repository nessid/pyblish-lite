name = 'pyblish_plugins_maya'

version = '0.3.0'

description = 'Pyblish commons plugins used in Maya software'

authors = ['vbeges', 'nessid']

requires = [
            'maya',
            'maya_lib-0.1+',
            'pyblish_base',
            'pyblish_core',
            ]

cachable = False


def commands():
    env.PYTHONPATH.append('{root}')
    env.PYBLISH_PLUGINS_FOLDERS.append('{root}/pyblish_plugins_maya/plugins')

    # IMPORTANT : Comment this command for deploy
    # env.PYBLISHPLUGINPATH.append('{root}/pyblish_plugins_maya/test_plugins')
