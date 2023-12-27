from .version import version, version_info, __version__

# This must be run prior to importing the application, due to the
# application requiring a discovered copy of Qt bindings.

from .app import show

__all__ = [
    'show',
    'version',
    'version_info',
    '__version__'
]

from .setup_env import setup_env_variables

setup_env_variables()
