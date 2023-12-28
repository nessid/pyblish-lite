import pyblish.api
import maya.cmds as cmds
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ModelHiSmoothSetsValidator(pyblish.api.Validator):
    """
    Model Hi | Smooth Sets Validator

    This Pyblish validator plugin checks whether MODEL_HI members are correctly assigned to exclusive smooth sets.

    This validator performs the following checks:
    1. It creates missing smooth sets (smooth0_set, smooth1_set, smooth2_set).
    2. It verifies that the nodes in the 'hi_set_nodes' instance are members of a smooth set.
    3. It reports nodes that are not in any smooth set and nodes that are members of multiple smooth sets.

    If any issues are found, appropriate actions are created to assist with the resolution.
    """
    plugin_id = 'a8aa1672-b71a-4f2f-8292-238ee95ba13b'  # https://www.uuidgenerator.net/version4
    category = 'Model Hi'
    name = 'Smooth sets'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.ValidatorOrder + 0.03

    def process(self, context):
        """
        Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve the hi_set_nodes from the context data
        hi_set_nodes = context.data['hi_set_nodes']

        # Create missing smooth sets (smooth0_set, smooth1_set, smooth2_set)
        not_hi_nodes = []
        for i in range(3):
            set_name = f"smooth{i}_set"
            if not cmds.objExists(set_name):
                # Create the set if it doesn't exist
                cmds.sets(name=set_name, empty=True)
            else:
                # Check if the members of the smooth set are from MODEL_HI set
                members = cmds.sets(set_name, query=True) or []
                for member in members:
                    if member not in hi_set_nodes:
                        not_hi_nodes.append(member)

        # Lists to store nodes that are not in any smooth set and nodes in multiple smooth sets
        no_smooth_set = []
        multiple_smooth_sets = []

        # Iterate through each node in hi_set_nodes
        for node in hi_set_nodes:
            node_in_smooth_set = []
            # Iterate through smooth sets (smooth0_set, smooth1_set, smooth2_set)
            for index in range(3):
                set_name = f'smooth{index}_set'

                # Check if the specific set exists
                set_exists = cmds.objExists(set_name)

                if not set_exists:
                    continue

                # Check if the node is a member of the current set
                if cmds.sets(node, isMember=set_name):
                    self.log.info(f'{node} is a member of {set_name}.')
                    node_in_smooth_set.append(set_name)

            # If the node is not in any smooth set, add it to no_smooth_set list
            if not node_in_smooth_set:
                no_smooth_set.append(node)
                self.log.warning(f'{node} is not a member of a smooth_set.')
            # If the node is in multiple smooth sets, add it to multiple_smooth_sets list
            elif len(node_in_smooth_set) > 1:
                multiple_smooth_sets.append(node)
                self.log.warning(f'{node} is a member of multiple smooth_sets : {node_in_smooth_set}')

        # Create 'Select' actions for nodes with issues
        if no_smooth_set:
            # Create 'Select' action subclass for nodes not in any smooth set
            select_no_smooth_set = actions.create_action_subclass(actions.Select,
                                                                  'hi mesh(es) not in smooth_sets',
                                                                  no_smooth_set
                                                                  )
            self.actions.append(select_no_smooth_set)

        if multiple_smooth_sets:
            # Create 'Select' action subclass for nodes in multiple smooth sets
            select_multiple_smooth_sets = actions.create_action_subclass(actions.Select,
                                                                         'hi mesh(es) in multiple smooth_sets',
                                                                         multiple_smooth_sets
                                                                         )
            self.actions.append(select_multiple_smooth_sets)

        if not_hi_nodes:
            # Create 'Select' action subclass for nodes in multiple smooth sets
            select_not_hi_nodes = actions.create_action_subclass(actions.Select,
                                                                 'non MODEL_HI member(s) in smooth_sets',
                                                                 not_hi_nodes
                                                                 )
            self.actions.append(select_not_hi_nodes)

        # Report validation result
        validation_result(self,
                          'hi mesh(es) with smooth_set issue',
                          no_smooth_set + multiple_smooth_sets + not_hi_nodes,
                          self.failure_response)
