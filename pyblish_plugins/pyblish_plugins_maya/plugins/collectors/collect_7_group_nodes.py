import pyblish.api
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import collection_result
from pyblish_core.name_lib import define_plugin_label


class TransformGroupNodesCollector(pyblish.api.Collector):
    """ Collect Transform | Group Nodes

    This Pyblish collector plugin retrieves the list of group nodes in the current Maya scene.
    Groups are transform nodes that are neither:
     - parents to a shape node
     - root nodes

    The collected list is added to the Pyblish context as 'group_nodes' data.
    """
    plugin_id = 'b0c44728-9a68-47db-a143-63e227109691'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Groups'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.43

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve the list of transform nodes from the context data
        transform_nodes = context.data['transform_nodes']

        # Retrieve the list of shape scope nodes from the context data
        shape_scope_nodes = context.data['shape_scope_nodes']

        # Retrieve the list of root nodes from the context data
        root_nodes = context.data['root_nodes']

        # Retrieve the list of GEO direct children from the context data
        geo_direct_children = context.data['geo_direct_children']

        group_nodes = list(set(transform_nodes)-set(shape_scope_nodes)-set(root_nodes)-set(geo_direct_children))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = group_nodes

        # Store data on the context
        context.data['group_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'group node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'group node(s)', collected_nodes)
