import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ReferenceNodesCollector(pyblish.api.Collector):
    """Collects all referenced nodes in the Maya scene.

    This Pyblish collector plugin retrieves reference nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'reference_nodes' data.
    """
    plugin_id = '0cdbeb0c-8407-4298-97c4-0d96c35c49e2'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Reference nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all referenced nodes in the scene
        reference_nodes = cmds.ls(references=True, long=True)

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = reference_nodes

        # Store data on the context
        context.data['reference_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'reference node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Report the collection result
        collection_result(self, 'reference node(s)', collected_nodes)
