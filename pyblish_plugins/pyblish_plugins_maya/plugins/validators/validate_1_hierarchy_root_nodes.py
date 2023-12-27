import pyblish.api
import maya.cmds as cmds
import re
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.results_lib import generate_result_message
from pyblish_core.name_lib import define_plugin_label


class CreateMissingRootNodes(pyblish.api.Action):
    """Create Missing Root Nodes

    This Pyblish action creates missing root nodes based on the validation results.

    """
    label = 'Create missing root nodes'
    on = 'failedOrWarning'  # The plug-in has been processed, and failed or had a warning

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The Pyblish plugin
        """
        created_root_nodes = []

        # List the already existing items from plugin.missing_required_root_nodes
        existing_required_root_nodes = cmds.ls(plugin.missing_required_root_nodes)

        # Remove already created root nodes from the list of missing nodes
        missing_required_root_nodes = list(set(plugin.missing_required_root_nodes) - set(existing_required_root_nodes))

        # Alphabetically sort the list
        missing_required_root_nodes.sort()

        for missing_required_root_node in missing_required_root_nodes:
            # Create a new transform node with the missing root node name
            cmds.createNode('transform', name=missing_required_root_node)
            created_root_nodes.append(missing_required_root_node)

        result_msg = generate_result_message('required root node(s)', created_root_nodes, 'created')
        self.log.info(result_msg)

        plugin.actions.remove(CreateMissingRootNodes)


class RootNodesValidator(pyblish.api.Validator):
    """Root nodes Validator

    This Pyblish validator plugin checks if the required root nodes are present in the current Maya scene.

    """
    plugin_id = 'e8a1589c-75e3-4ad8-8284-23a922d5d74e'  # https://www.uuidgenerator.net/version4
    category = 'Hierarchy'
    name = 'Root nodes'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    actions = []  # The actions will be populated dynamically based on validation results

    # Class attributes for interoperability with Pyblish actions:
    missing_required_root_nodes = []
    invalid_root_nodes = []

    def process(self, context):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        print(f"{self.label} failure response: {self.failure_response}")

        # Clear class attributes
        self.missing_required_root_nodes.clear()
        self.invalid_root_nodes.clear()

        # Retrieve the list of nodes from the context data
        root_nodes = context.data['root_nodes']

        # Retrieve root nodes short names
        root_nodes = cmds.ls(root_nodes, long=False)

        # Retrieve required root nodes
        required_root_nodes = context.data['required_root_nodes']

        # Retrieve valid root nodes
        valid_root_nodes = context.data['valid_root_nodes']

        renamable_nodes = {}

        # Required root nodes
        for required_root_node in required_root_nodes:
            if required_root_node.lower() not in [item.lower() for item in root_nodes]:
                self.missing_required_root_nodes.append(required_root_node)
                continue

            for root_node in root_nodes:
                if root_node.lower() == required_root_node.lower():
                    if not root_node.isupper():
                        renamable_nodes[root_node] = root_node.upper()

        # If missing required root nodes are found, add the CreateMissingRootNodes action
        if self.missing_required_root_nodes:
            self.actions.append(CreateMissingRootNodes)

        # Invalid root nodes
        for root_node in root_nodes:
            if root_node in required_root_nodes:
                continue

            is_valid = False
            for valid_root_node in valid_root_nodes:
                pattern = re.compile(rf"{valid_root_node}\d*$", re.IGNORECASE)
                match = pattern.search(root_node)
                if not match:
                    continue

                if root_node.isupper():
                    is_valid = True
                else:
                    renamable_nodes[root_node] = root_node.upper()
                    self.log.warning(f"'{root_node}' is a valid root name but it should be upper case.")

            if not is_valid:
                self.invalid_root_nodes.append(root_node)

        if self.invalid_root_nodes:
            # Create 'Select' actions subclass for invalid root node(s)
            select_invalid_root_nodes = actions.create_action_subclass(actions.Select,
                                                                       'invalid root node(s)',
                                                                       self.invalid_root_nodes
                                                                       )
            self.actions.append(select_invalid_root_nodes)

        if renamable_nodes:
            # Create 'Rename' actions subclass for failed root node(s)
            rename_failed_root = actions.create_action_subclass(actions.Rename,
                                                                'root node(s)',
                                                                renamable_nodes
                                                                )
            self.actions.append(rename_failed_root)

        validation_result(self, 'missing root node(s)', self.missing_required_root_nodes, 'warning')
        validation_result(self, 'invalid root node(s)', self.invalid_root_nodes, 'warning')

        validation_result(self, 'root node(s) issue(s)',
                          self.missing_required_root_nodes + self.invalid_root_nodes,
                          self.failure_response)
