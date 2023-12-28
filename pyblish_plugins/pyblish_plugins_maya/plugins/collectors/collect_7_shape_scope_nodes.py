import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class TransformShapeNodesCollector(pyblish.api.Collector):
    """ Collect | Shape Scopes

    This Pyblish collector plugin retrieves the list of shape scopes (parents of shape nodes) in the current Maya scene.

    The collected list is added to the Pyblish context as 'group_nodes' data.
    """
    plugin_id = 'c539045f-0905-4c62-b118-00c97bbcfe29'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Shape scopes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.42

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve shape nodes from the context data
        shape_nodes = context.data['shape_nodes']

        # List relatives of the shape nodes to get their parent transform nodes
        shape_scope_nodes = cmds.listRelatives(shape_nodes, parent=True, fullPath=True) or []

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = shape_scope_nodes

        # Store data on the context
        context.data['shape_scope_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'shape scope(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'shape scope(s)', collected_nodes)
