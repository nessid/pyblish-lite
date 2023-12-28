import pyblish.api
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class LayersValidator(pyblish.api.Validator):
    """Validator to check if there are layers in the scene.

    If a layer node is identified, it is considered a failed node and can be selected or deleted using the associated actions.

    """
    plugin_id = '23f1b8ad-6928-45e1-8c80-c8f4c5b07fd8'  # https://www.uuidgenerator.net/version4
    category = 'Clean'
    name = 'Custom layers'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.ValidatorOrder + 0.01

    def process(self, context):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve the list of nodes from the context data
        layer_nodes = context.data['layer_nodes']

        # Retrieve nodes to be excluded from validation
        excluded_nodes = context.data['excluded_nodes']

        # Filter out the excluded nodes from the collected layer nodes
        nodes = list(set(layer_nodes) - set(excluded_nodes))

        failed_nodes = nodes

        # Actions
        if failed_nodes:
            # Create 'Select' actions subclass for failed node(s)
            select_layers = actions.create_action_subclass(actions.Select,
                                                           'custom layer(s)',
                                                           failed_nodes
                                                           )
            self.actions.append(select_layers)

            # Create 'Delete' actions subclass for failed node(s)
            delete_layers = actions.create_action_subclass(actions.Delete,
                                                           'custom layer(s)',
                                                           failed_nodes
                                                           )
            self.actions.append(delete_layers)

        validation_result(self, 'custom layer(s)', failed_nodes, self.failure_response)
