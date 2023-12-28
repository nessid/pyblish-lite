import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class DefaultNodesCollector(pyblish.api.Collector):
    """Collects Maya default nodes that are neither deletable nor locked.

    This Pyblish collector plugin retrieves default nodes in the current Maya scene that cannot be deleted and are not locked.
    These nodes typically represent built-in or default settings.

    The collected list is added to the Pyblish context as 'default_nodes' data.
    """
    plugin_id = 'ddc43e4d-4c06-45d9-b46d-80c35d5ccaa7'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Maya\'s default nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List undeletable nodes
        undeletable_nodes = cmds.ls(undeletable=True, long=True)

        # List locked nodes
        locked_nodes = cmds.ls(lockedNodes=True, long=True)

        # Remove locked nodes from undeletable nodes to get final list
        nodes = list(set(undeletable_nodes) - set(locked_nodes))

        collected_nodes = []

        # Store the collected nodes for use in other plugins or actions
        collected_nodes[:] = nodes

        # Store data on the context
        context.data['default_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'Maya\'s default node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Report the collection result
        collection_result(self, 'Maya default node(s)', collected_nodes)
