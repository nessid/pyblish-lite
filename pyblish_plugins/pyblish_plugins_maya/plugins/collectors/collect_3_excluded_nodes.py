import pyblish.api
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ExcludeFromValidationCollector(pyblish.api.Collector):
    """
    This Pyblish collector plugin retrieves nodes in the current Maya scene
    that should be excluded from further validation by validators.

    The collected list is added to the Pyblish context as 'excluded_nodes' data.
    """
    plugin_id = '9180acb1-9953-47b2-aa90-a0885a92c0e8'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Excluded nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.2

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        exclusion_list = [
            'default_nodes',
            'reference_nodes',
            'reference_members_nodes',
            'trash_nodes',
            'help_nodes',
            'previz_nodes',
        ]

        collected_nodes = []

        # Retrieve exclusion_list nodes from context data
        for context_data in exclusion_list:
            nodes = context.data[context_data]
            if nodes:
                collected_nodes.extend(nodes)

        # Store nodes to exclude from validation in the context data
        context.data['excluded_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'excluded node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'node(s) to exclude from validation', collected_nodes)
