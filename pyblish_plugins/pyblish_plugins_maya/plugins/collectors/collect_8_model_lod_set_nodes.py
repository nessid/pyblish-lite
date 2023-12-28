import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class LodMeshNodesCollector(pyblish.api.Collector):
    """ Collect | LOD Sets Nodes

    This Pyblish collector plugin retrieves the list of hi shape nodes in the current Maya scene.

    The collected list is added to the Pyblish context as 'hi_shape_nodes' data.
    """
    plugin_id = '886355db-634e-4864-a7d9-60b7fb0efea1'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'LOD sets nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.43

    @staticmethod
    def _define_lod_set_name(lod_type):
        return f"MODEL_{lod_type.upper()}"

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        lod_types = context.data['lod_types']

        for lod_type in lod_types:
            set_name = self._define_lod_set_name(lod_type)
            if cmds.objExists(set_name):
                lod_set_nodes = cmds.sets(set_name, query=True) or []
            else:
                lod_set_nodes = []

            collected_nodes = lod_set_nodes

            # Store data in context
            context.data[f'{lod_type}_set_nodes'] = collected_nodes

            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    f'{lod_type} set node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

            # Provide information about the collection in the result
            collection_result(self, f'{lod_type} set node(s)', collected_nodes)
