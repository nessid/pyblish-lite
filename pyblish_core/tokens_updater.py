# import logging
# import pyblish.api
# from engines_software_manager.software_engine import SoftwareEngine
# from template_manager_core.templated_path import TemplatedPath
from pyblish_core import plugins_collection, plugins_registration
from pyblish_core.logging import configure_logging
from pyblish.api import (
    deregister_all_paths,
    deregister_all_plugins
    )

log = configure_logging(__name__)


class TokensUpdater:
    def __init__(self):
        self.previous_filepath = None  # Stores the last processed file path
        self.previous_tokens = None  # Stores tokens related to the file path

    # def _filepath_has_changed(self, current_filepath):
    #     # Compares the current file path with the previous one to detect changes
    #     if current_filepath != self.previous_filepath:
    #         log.info(f"File path has changed since the last reset: {self.previous_filepath} >> {current_filepath}")
    #         return True
    #     else:
    #         log.info("File path has not changed since the last reset.")
    #         return False
    #
    # def _get_current_tokens(self):
    #     """
    #      Retrieves the current asset task by extracting and parsing the file path from the software engine.
    #
    #      Returns:
    #      tuple: A tuple containing the asset type and task, or None if not found or an error occurs.
    #      """
    #
    #     # Retrieve the current software engine and use it to retrieve the current filepath
    #     engine = SoftwareEngine.from_environment_context()
    #     filepath = engine.get_filepath()
    #
    #     # Validate the existence of the file path
    #     if filepath is None:
    #         raise pyblish.api.ValidationError('Instance has no \'scene_path\' data')
    #         return
    #
    #     # Ensure the file path is not empty (indicating an unsaved scene)
    #     if not filepath:
    #         raise pyblish.api.ValidationError('The scene must be saved before running this check')
    #         return
    #
    #     log.info(f"File path collected: {filepath}")
    #
    #     # Check if the current file path has changed compared to the previous check
    #     filepath_has_changed = self._filepath_has_changed(filepath)
    #
    #     if filepath_has_changed:
    #         # If the path has changed, attempt to create a TemplatedPath instance from the new path
    #         templated_path = TemplatedPath.from_path_only(filepath)
    #
    #         # Check if the created TemplatedPath instance is None (not templated)
    #         if templated_path is None:
    #             raise pyblish.api.PyblishError(f"Invalid filepath: no templated path found for '{filepath}'")
    #             return
    #
    #         # Log a message indicating a valid templated path
    #         log.info(f"Valid filepath: '{templated_path.template}' templated path found for '{filepath}'")
    #
    #         # Update tokens with those extracted from the new TemplatedPath
    #         tokens = templated_path.tokens
    #         self.previous_tokens = tokens
    #
    #     else:
    #         # If the file path hasn't changed, reuse the previously stored tokens
    #         tokens = self.previous_tokens
    #
    #     # Update the stored previous file path to the current one for future comparisons
    #     self.previous_filepath = filepath
    #
    #     return tokens

    def register_plugins_by_task(self, asset_type=None, task=None):
        """
        Registers Pyblish plugins based on the current asset type and task.
        """

        # Clear any previously registered plugin paths and plugins
        deregister_all_paths()
        deregister_all_plugins()

        # Retrieve current tokens
        # tokens = self._get_current_tokens()
        # tokens = {
        #     'asset_type': 'Set',
        #     'task': 'model_all',
        #           }

        # Check if tokens are retrieved
        if asset_type and task:
            # Extract asset type and task from tokens
            # asset_type = tokens['asset_type']
            # task = tokens['task']

            # Create a collection of plugins specific to the current asset type and task
            collection = plugins_collection.PluginsCollect.from_asset_task(asset_type, task)

            # Register the created collection of plugins for use in the Pyblish system
            plugins_registered = plugins_registration.PluginsRegister(collection)
            plugins_registered.register()

            # Log the successful registration of plugins for the specific asset type and task
            log.info(f"Successfully registered Pyblish plugins for asset type '{asset_type}' and task '{task}'.")
        else:
            # Log a message if no valid asset type and task were found, indicating no plugins were registered
            log.info('Unable to register Pyblish plugins: no asset type or task information available.')


