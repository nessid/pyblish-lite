import pyblish.api
from engines_software_manager.software_engine import SoftwareEngine
from pyblish_core.name_lib import define_plugin_label
from pyblish_core.plugins_results import collection_result


class CurrentFilePathCollector(pyblish.api.Collector):
    """Collect the file path of the current scene.

    This Pyblish collector plugin retrieves the file path of the current scene and adds it to
    the Pyblish context as an instance with 'scene_path' data.
    """
    plugin_id = '509a0ea1-9c6a-412b-8332-d2763dc893f1'
    category = 'Scene Context'
    name = 'Current file path'

    hosts = ['*']
    mandatory = True

    label = define_plugin_label(category, name)

    def process(self, context):
        """Main method for processing the current context

        :param context: The Pyblish context used for collecting and publishing data
        """
        try:
            # Retrieve the file path of the current scene from the engine
            engine = SoftwareEngine.from_environment_context()
            filepath = engine.get_filepath()

            # Create an instance in the Pyblish context with a dynamic name
            instance_name = 'Current file path'
            instance = context.create_instance(instance_name)

            # Add data to the created instance
            instance.data['families'] = ['scene_context']
            instance.data['scene_path'] = filepath
            if filepath:
                self.log.info(f"Scene path collected: {filepath}")
            else:
                self.log.warning("No filepath found")
        except Exception as e:
            # Handle any errors or exceptions here (e.g., log an error message)
            self.log.error(f"Failed to collect scene path: {str(e)}")

        collection_result(self, 'current filepath(s)', filepath)
