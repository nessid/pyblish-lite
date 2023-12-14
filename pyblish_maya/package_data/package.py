# -*- coding: utf-8 -*-

name = 'pyblish_maya'

version = '2.1.10'

description = 'Maya Pyblish package'

authors = ['Abstract Factory and Contributors marcus@abstractfactory.io']

requires = [
    'pyblish_base-1.4+',
    # 'pyblish_qml-1.11+',
]

# WARNING
# Default plugins that were originally included have been relocated to {root}/python/pyblish_maya/legacy_plugins

def commands():
    env.PYTHONPATH.append('{root}/python')
    env.PYTHONPATH.append('{root}/python/pyblish_maya')
    env.MAYA_SCRIPT_PATH.append('{root}/python/pyblish_maya/pythonpath')


help = [['Home Page', 'https://github.com/pyblish/pyblish-maya']]
