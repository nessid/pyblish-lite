import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ShapeNodesCollector(pyblish.api.Collector):
    """ Collect shape nodes

    This Pyblish collector plugin retrieves the list of shape nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'shape_nodes' data.
    """
    plugin_id = '0db45f7f-bab0-4ca2-91ae-6cfd3bc10e7a'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Shape nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all shape nodes in the scene
        nodes = cmds.ls(shapes=True, long=True)

        # Retrieve nodes to be excluded from validation
        excluded_nodes = context.data['excluded_nodes']

        # Filter out the excluded nodes from the collected shape nodes
        nodes = list(set(nodes) - set(excluded_nodes))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data['shape_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'shape node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'shape node(s)', collected_nodes)
