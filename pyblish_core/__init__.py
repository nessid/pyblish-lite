import os
import pyblish.api
from pyblish_core.filepath_tokens_updater import FilepathTokensUpdater
from .lib import configure_logging

log = configure_logging(__name__)

# Instantiate FilepathTokensUpdater
filepath_tokens_updater = FilepathTokensUpdater()
log.info('Instantiate FilepathTokensUpdater')


def on_pyblish_lite_reset():
    log.info('on_pyblish_lite_reset')
    asset_type = os.getenv('PYBLISH_LITE_ASSET_TYPE')
    task = os.getenv('PYBLISH_LITE_TASK')
    filepath_tokens_updater.register_plugins_by_task(asset_type, task)


pyblish.api.register_callback("pyblish_lite_reset", on_pyblish_lite_reset)
