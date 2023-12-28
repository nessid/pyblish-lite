import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class GeoDirectChildrenCollector(pyblish.api.Collector):
    """ Collect GEO Direct children

    This Pyblish collector plugin retrieves the list of GEO root direct children in the current Maya scene.

    The collected list is added to the Pyblish context as 'geo_direct_children' instances.
    """
    plugin_id = '53fd9a03-0a42-4635-a014-59aa17b9f468'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Geo direct children'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.4

    def process(self, context):
        """Main method for processing the current context.

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        geo_direct_children = []
        model_lod_types = []

        # Collect Geo direct children
        if cmds.ls('|GEO'):
            # List all direct children of the node
            geo_direct_children = cmds.listRelatives('|GEO', children=True, fullPath=True) or []

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = geo_direct_children

        # Store data on the context
        context.data['geo_direct_children'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'GEO direct child(ren)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'GEO direct child(ren)', collected_nodes)

        # Collect MODEL_LOD types
        lod_types = context.data['lod_types']

        for lod_type in lod_types:
            if f"MODEL_{lod_type.upper()}_grp" in cmds.ls(geo_direct_children, long=False):
                model_lod_types.append(lod_type)

        context.data['model_lod_types'] = model_lod_types

        if model_lod_types:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'model LOD type(s)',
                                                                    model_lod_types
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'model LOD type(s)', model_lod_types)
