import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import collection_result
from pyblish_core.name_lib import define_plugin_label


class MeshNodesCollector(pyblish.api.Collector):
    """ Collect mesh nodes

    This Pyblish collector plugin retrieves the list of mesh nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'mesh_nodes' data.
    """
    plugin_id = 'c4d87ba8-d612-416d-aedb-9a64ba1b5a22'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Mesh nodes'

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
        shape_nodes = cmds.ls(shapes=True, long=True)

        # Filter the nodes to only include mesh nodes
        mesh_nodes = cmds.ls(shape_nodes, type='mesh', long=True) or []

        # Retrieve nodes to be excluded from validation
        excluded_nodes = context.data['excluded_nodes']

        # Filter out the excluded nodes from the collected shape nodes
        nodes = list(set(mesh_nodes) - set(excluded_nodes))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data['mesh_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'mesh node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'mesh node(s)', collected_nodes)
