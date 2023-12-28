import fnmatch
import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class PrevizNodesCollector(pyblish.api.Collector):
    """ Collect Previz Nodes

    This Pyblish collector plugin retrieves previz nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'previz_nodes' data.
    """
    plugin_id = 'bb05e8a5-41f0-446f-b458-bc7be6e6c248'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Previz nodes'

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
        pattern = '*previz'

        pattern_nodes = []

        # Use fnmatch to filter nodes matching the pattern (case-insensitive)
        pattern_nodes.extend([node for node in all_nodes if fnmatch.fnmatch(node.lower(), pattern.lower())])

        # Also check for nodes with "_grp" suffix
        pattern_nodes.extend([node for node in all_nodes if fnmatch.fnmatch(node.lower(), (pattern + '_grp').lower())])

        collected_nodes = []

        if pattern_nodes:
            # Collect all descendants of the matched nodes
            collected_nodes[:] = cmds.listRelatives(pattern_nodes, allDescendents=True, fullPath=True) or []

        # Store data on the context
        context.data['previz_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'previz node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Report the collection result
        collection_result(self, 'previz node(s)', collected_nodes)
