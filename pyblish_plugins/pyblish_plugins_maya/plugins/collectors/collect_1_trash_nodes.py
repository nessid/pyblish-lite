import fnmatch
import maya.cmds as cmds
import pyblish.api
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class TrashNodesCollector(pyblish.api.Collector):
    """ Collect Trash Nodes

    This Pyblish collector plugin retrieves the list of trash nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'trash_nodes' data.
    """
    plugin_id = '42ec5c5c-a439-4679-b5c9-6f4bf3d091ff'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Trash nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all nodes in the scene
        all_nodes = cmds.ls(long=True)

        # Define the pattern to match (case-insensitive)
        pattern = '*trash'

        pattern_nodes = []

        # Use fnmatch to filter nodes matching the pattern (case-insensitive)
        pattern_nodes.extend([node for node in all_nodes if fnmatch.fnmatch(node.lower(), pattern.lower())])

        # Also check for nodes with "_grp" suffix
        pattern_nodes.extend([node for node in all_nodes if fnmatch.fnmatch(node.lower(), pattern+'_grp'.lower())])

        collected_nodes = []

        if pattern_nodes:
            # If matching nodes are found, collect all descendants with their full paths
            collected_nodes[:] = cmds.listRelatives(pattern_nodes, allDescendents=True, fullPath=True) or []

        # Store data on the context
        context.data['trash_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'trash node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Report the collection result
        collection_result(self, 'trash node(s)', collected_nodes)
