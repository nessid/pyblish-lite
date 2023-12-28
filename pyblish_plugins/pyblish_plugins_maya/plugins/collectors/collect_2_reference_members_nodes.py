import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ReferenceMembersCollector(pyblish.api.Collector):
    """Collects all referenced nodes in the Maya scene.

    This Pyblish collector plugin retrieves all members of the reference nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'reference_members_nodes' data.
    """
    plugin_id = '84dae1c8-e4a8-48cc-85fa-8c915370450d'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Reference members'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.1

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve reference nodes from the instance
        reference_nodes = context.data['reference_nodes']

        # Create a list to store reference members
        reference_members = []

        for reference_node in reference_nodes:
            try:
                # Get the filename associated with the reference node
                reference_filename = cmds.referenceQuery(reference_node, filename=True)
                if reference_filename:
                    self.log.info(f"Reference node '{reference_node}' filename : {reference_filename}")

                    # Use referenceQuery to get the nodes associated with the reference
                    nodes_in_reference = cmds.referenceQuery(reference_node, nodes=True) or []

                    # Extend the list of reference members with the nodes in the reference
                    reference_members.extend(nodes_in_reference)
                else:
                    self.log.warning(f"Reference node '{reference_node}' has no filename")

            except Exception as e:
                self.log.warning(f"Error processing reference node '{reference_node}': {str(e)}")

        # Retrieve reference members using long names
        reference_members = cmds.ls(reference_members, long=True)

        collected_nodes = []

        # Store the collected nodes for use in other plugins or actions
        collected_nodes[:] = reference_members

        # Store data on the context
        context.data['reference_members_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'reference member(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'reference member(s)', collected_nodes)
