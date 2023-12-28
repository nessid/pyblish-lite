import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class EmptyGroupsValidator(pyblish.api.Validator):
    """Empty Groups Validator

    This Pyblish validator plugin checks whether empty groups exist in the current Maya scene.
    Empty groups are transform nodes that do not contain any shape nodes or child transform nodes.

    If empty groups are found, they are considered failed nodes and can be selected or deleted using the associated actions.

    """
    plugin_id = '6ba82b4e-de9e-41a1-b235-1a45a393810c'  # https://www.uuidgenerator.net/version4
    category = 'Clean'
    name = 'Empty groups'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.01

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of nodes from the context data
        transform_nodes = context.data['transform_nodes']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Find the common elements between geo nodes and shape nodes
        nodes = list(set(model_nodes).intersection(transform_nodes))

        # Retrieve the list of required root nodes from the context data
        required_root_nodes = context.data['required_root_nodes']

        # Exclude root nodes from transform nodes
        nodes = list(set(nodes) - set(required_root_nodes))

        failed_nodes = []

        if nodes:
            # Sort the list of nodes by their length in descending order.
            # This ensures that longer node names appear before shorter ones, helping
            # to select nodes with longer, more specific names that match the pattern.
            nodes = sorted(nodes, key=len, reverse=True)

            for node in nodes:
                children = cmds.listRelatives(node, children=True, allDescendents=True) or []
                if cmds.ls(children, shapes=True):
                    continue

                failed_nodes.append(node)

        if failed_nodes:
            # Create 'Select' actions subclass for empty groups
            select_empty_groups = actions.create_action_subclass(actions.Select,
                                                                 'empty group(s)',
                                                                 failed_nodes
                                                                 )
            self.actions.append(select_empty_groups)

            # Create 'Delete' actions subclass for empty groups
            delete_empty_groups = actions.create_action_subclass(actions.Delete,
                                                                 'empty group(s)',
                                                                 failed_nodes
                                                                 )
            self.actions.append(delete_empty_groups)

        validation_result(self, 'empty group(s)', failed_nodes, self.failure_response)
