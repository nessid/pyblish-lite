import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class RootNodesCollector(pyblish.api.Collector):
    """
    Collects root nodes.

    This Pyblish collector plugin retrieves root nodes from the current Maya scene.

    The collected list is added to the Pyblish context as 'root_nodes' data.
    """
    plugin_id = '042de368-d1ed-49e7-9e04-fe0008ed0dea'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Root nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):
        """
        Main method for processing the current context.

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List root nodes
        root_nodes = cmds.ls(assemblies=True, long=True)

        # Retrieve nodes to be excluded from validation (expected to be a list)
        excluded_nodes = context.data['excluded_nodes']

        # Filter out the excluded nodes from the collected nodes
        nodes = list(set(root_nodes) - set(excluded_nodes))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data['root_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'root node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Report the collection result
        collection_result(self, 'root node(s)', collected_nodes)
