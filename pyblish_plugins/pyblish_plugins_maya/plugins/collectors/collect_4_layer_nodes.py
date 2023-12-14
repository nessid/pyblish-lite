import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import collection_result
from pyblish_core.name_lib import define_plugin_label


class LayerNodesCollector(pyblish.api.Collector):
    """ Collect layer nodes

    This Pyblish collector plugin retrieves the list of layer nodes in the current Maya scene, excluding Maya's default nodes.

    The collected list is added to the Pyblish context as 'layer_nodes' data.
    """
    plugin_id = '5d118872-61e7-4235-8fb6-01d1393e8710'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Layer nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all nodes in the scene with the exact type 'displayLayer'
        nodes = cmds.ls(exactType='displayLayer', long=True)

        # Retrieve nodes to be excluded from validation
        excluded_nodes = context.data['excluded_nodes']

        # Filter out the excluded nodes from the collected layer nodes
        nodes = list(set(nodes) - set(excluded_nodes))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data['layer_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'layer node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'layer node(s)', collected_nodes)
