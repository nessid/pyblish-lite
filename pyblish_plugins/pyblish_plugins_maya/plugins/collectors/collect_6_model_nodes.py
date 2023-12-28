import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ModelLodNodesCollector(pyblish.api.Collector):
    """ Collect Model LOD Nodes

    This Pyblish collector plugin retrieves the list of all model LOD nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'model_{lod_type}_nodes' instances.
    """
    plugin_id = '68bd659c-4bdc-48ca-915d-caa2e76dc44f'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Model LOD nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.41

    def process(self, context):
        """Main method for processing the current context.

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        lod_types = context.data['lod_types']

        excluded_nodes = context.data['excluded_nodes']

        geo_direct_children = context.data['geo_direct_children']

        model_nodes_lod_mapping = {}

        if cmds.ls('|GEO'):
            geo_nodes = cmds.listRelatives('|GEO', allDescendents=True, fullPath=True) or []

            model_nodes = list(set(geo_nodes) - set(excluded_nodes) - set(geo_direct_children))

            for lod_type in lod_types:
                model_nodes_lod_mapping[lod_type] = []

            for model_node in model_nodes:
                short_name = model_node.split('|')[-1]
                short_name_patterns = short_name.split('_')

                # Use set intersection to find common elements
                node_lod_types = list(set(short_name_patterns) & set(lod_types))

                for node_lod_type in node_lod_types:
                    model_nodes_lod_mapping[node_lod_type].append(model_node)

            for lod_type in lod_types:
                # Store the collected nodes for use in other plugins or actions
                collected_nodes = model_nodes_lod_mapping[lod_type]

                if collected_nodes:
                    # Store data in an instance
                    instance = context.create_instance(f"MODEL {lod_type.upper()} nodes ({len(collected_nodes)})")
                    instance.data['families'] = [f'model_{lod_type}_nodes']
                    instance.data['nodes'] = collected_nodes

                    # Create 'Select' actions subclass for collected nodes
                    select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                            f'MODEL_{lod_type.upper()} node(s)',
                                                                            collected_nodes
                                                                            )
                    self.actions.append(select_collected_nodes)

                # Provide information about the collection in the result
                collection_result(self, f'MODEL_{lod_type.upper()} node(s)', collected_nodes)

            # Store data in an instance
            instance = context.create_instance(f"MODEL nodes ({len(model_nodes)})")
            instance.data['families'] = [f'model_nodes']
            instance.data['nodes'] = model_nodes

            # Create 'Select' actions subclass for collected nodes
            select_model_nodes = actions.create_action_subclass(actions.Select,
                                                                f'MODEL node(s)',
                                                                model_nodes
                                                                )
            self.actions.append(select_model_nodes)

            # Provide information about the collection in the result
            collection_result(self, f'MODEL node(s)', model_nodes)
