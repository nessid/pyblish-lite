# import pyblish.api
# from template_manager_core.templated_path import TemplatedPath
# from pyblish_core.name_lib import define_plugin_label
#
#
# class CurrentFilePathValidator(pyblish.api.Validator):
#     """Validate the current scene file path.
#
#     This Pyblish validator plugin checks and validates the "scene_path" data of an instance,
#     ensuring it is a templated path.
#
#     It raises an exception if the path is not templated.
#     """
#     plugin_id = '0fc25d8c-77c4-4cf4-9e44-e086f503da0a'
#     category = 'Scene Context'
#     name = 'Current file path'
#
#     hosts = ['*']
#     mandatory = True
#
#     label = define_plugin_label(category, name)
#
#     families = ['scene_context']
#
#     def process(self, instance):
#         """Main method for processing the current instance
#
#         :param instance: Instance that meets the plugin requirements
#         """
#         # Get the "scene_path" data from the instance
#         path = instance.data.get("scene_path")
#
#         # Check if the "scene_path" data is missing
#         if path is None:
#             raise pyblish.api.ValidationError('Instance has no \'scene_path\' data')
#
#         # Check if the "scene_path" data is an empty string (unsaved scene)
#         if not path:
#             raise pyblish.api.ValidationError('The scene must be saved before running this check')
#
#         # Attempt to create a TemplatedPath instance from the path
#         templated_path = TemplatedPath.from_path_only(path)
#
#         # Check if the created TemplatedPath instance is None (not templated)
#         if templated_path is None:
#             msg = f"Invalid filepath: no templated path found for '{path}'"
#             if self.failure_response == 'fail':
#                 raise pyblish.api.PyblishError(msg)
#             elif self.failure_response == 'warning':
#                 self.log.warning(msg)
#
#         # Log a message indicating a valid templated path
#         self.log.info(f"Valid filepath: '{templated_path.template}' templated path found for '{path}'")
