import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class TransformNodesCollector(pyblish.api.Collector):
    """ Collect transform nodes

    This Pyblish collector plugin retrieves the list of transform nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'transform_nodes' data.
    """
    plugin_id = '6f8fbb94-0198-4227-9355-f701da3d75ee'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Transform nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all transform nodes in the scene
        nodes = cmds.ls(exactType='transform', long=True)

        # Retrieve nodes to be excluded from validation
        excluded_nodes = context.data['excluded_nodes']

        # Filter out the excluded nodes from the collected transform nodes
        nodes = list(set(nodes) - set(excluded_nodes))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data['transform_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'transform node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'transform node(s)', collected_nodes)
