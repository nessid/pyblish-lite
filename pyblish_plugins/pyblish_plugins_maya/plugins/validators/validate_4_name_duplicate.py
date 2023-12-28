import pyblish.api
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class NameDuplicatedNodeNameValidator(pyblish.api.Validator):
    """Name | Duplicated Node Name Validator

    This Pyblish validator plugin checks if several nodes have the same short name.

    This validator identifies and reports nodes with duplicated name as failed nodes.

    """
    plugin_id = 'a7afc5bf-99ba-440c-b19d-603344290f5c'  # https://www.uuidgenerator.net/version4
    category = 'Name'
    name = 'Duplicated short name'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.023

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Retrieve excluded nodes from context
        excluded_node = context.data['excluded_nodes']

        nodes = list(set(model_nodes) - set(excluded_node))

        failed_nodes = []

        # Collect all short names
        short_names = [node.split('|')[-1] for node in nodes]

        # Find duplicates
        duplicate_short_names = [name for name in short_names if short_names.count(name) > 1]

        failed_nodes[:] = duplicate_short_names

        # Actions
        if failed_nodes:
            # Create 'Select' actions subclass for failed node(s)
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'node(s) with duplicated short name',
                                                                 failed_nodes
                                                                 )

            self.actions.append(select_failed_nodes)

        validation_result(self, 'node(s) with duplicated short name', failed_nodes, self.failure_response)
