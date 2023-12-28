import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ShadingGroupNodesCollector(pyblish.api.Collector):
    """Collect shading group nodes

    This Pyblish collector plugin retrieves shading groups (shading engines) in the current Maya scene.
    Shading groups represent the assignment of materials to objects.

    The collected list is added to the Pyblish context as 'shading_groups' data.
    """
    plugin_id = '6b6b90ea-8499-458f-bdfe-d1d82c1b35f6'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Shading group nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all nodes in the scene with the type 'shadingEngine'
        nodes = cmds.ls(type='shadingEngine', long=True)

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data["shading_groups"] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'shading group(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'shading group(s)', collected_nodes)
