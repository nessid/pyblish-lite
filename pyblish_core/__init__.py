import pyblish.api
from pyblish_core.filepath_tokens_updater import FilepathTokensUpdater
from .lib import configure_logging

log = configure_logging(__name__)

# Instantiate FilepathTokensUpdater
filepath_tokens_updater = FilepathTokensUpdater()
log.info('Instantiate FilepathTokensUpdater')


def on_pyblish_lite_reset():
    log.info('on_pyblish_lite_reset')
    filepath_tokens_updater.register_plugins_by_task()


pyblish.api.register_callback("pyblish_lite_reset", on_pyblish_lite_reset)
