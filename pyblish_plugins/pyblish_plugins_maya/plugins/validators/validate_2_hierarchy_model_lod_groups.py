import pyblish.api
import maya.cmds as cmds
import re
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.name_lib import find_pattern
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


class ModelLodGroupsValidator(pyblish.api.Validator):
    """Model LOD Groups Validator

    This Pyblish validator plugin checks if the Model LOD groups (GEO direct children) in the current Maya scene have the required format:
    MODEL_{LOD_TYPE}_grp or .*HELP

    NOTE : This plugin is not to be used with Characters
    """
    plugin_id = '2178703d-7d26-4aab-a42f-6075f9a59d39'  # https://www.uuidgenerator.net/version4
    category = 'Hierarchy'
    name = 'Model LOD groups'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.ValidatorOrder + 0.005

    def process(self, context):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve the list of nodes from the context data
        geo_direct_children = context.data['geo_direct_children']

        # Retrieve the LOD type from the context data
        lod_types = context.data['lod_types']

        shape_scopes = context.data['shape_scope_nodes']

        valid_geo_direct_children = []
        failed_geo_direct_children = []

        renamable_nodes = {}

        for node in geo_direct_children:
            # Retrieve node short name
            node_name_short = node.split('|')[-1]

            if node in shape_scopes:
                failed_geo_direct_children.append(node)
                self.log.warning(f"'{node}' is a shape scope. "
                                 f"GEO direct children must be groups named 'MODEL_(LOD_TYPE)_grp.")
                continue

            name_is_valid = False

            for lod_type in lod_types:
                if node_name_short == f"MODEL_{lod_type.upper()}_grp":
                    name_is_valid = True

            pattern = re.compile(rf".HELP\d*$")
            match = pattern.search(node_name_short)
            if match:
                name_is_valid = True

            if name_is_valid:
                valid_geo_direct_children.append(node)
            else:
                failed_geo_direct_children.append(node)

                node_lod_types = []
                for lod_type in lod_types:
                    node_lod_types.extend(find_pattern(node_name_short, lod_type))
                if len(node_lod_types) == 1 and len(find_pattern(node_name_short, 'model')) == 1:
                    new_name_short = f"MODEL_{node_lod_types[0].upper()}_grp"
                    new_name_long = node.replace(node_name_short, new_name_short)

                    if cmds.ls(new_name_long):
                        self.log.warning(f"'{new_name_long}' already exists. '{node}' can't be renamed.")
                    else:
                        renamable_nodes[node] = new_name_short
                else:
                    self.log.warning(f"'{node}' is not a valid name."
                                     f"GEO direct children must be groups named 'MODEL_(LOD_TYPE)_grp.")

        # Actions
        if failed_geo_direct_children:
            # Create 'Select' actions subclass for failed subgroup(s)
            select_failed_geo_direct_children = actions.create_action_subclass(actions.Select,
                                                                               'invalid geo_subgroup(s)',
                                                                               failed_geo_direct_children
                                                                               )
            self.actions.append(select_failed_geo_direct_children)

        if renamable_nodes:
            # Create 'Rename' actions subclass for failed subgroup(s)
            rename_failed_geo_direct_children = actions.create_action_subclass(actions.Rename,
                                                                               'invalid geo_subgroup(s)',
                                                                               renamable_nodes
                                                                               )
            self.actions.append(rename_failed_geo_direct_children)

        validation_result(self, 'invalid geo subgroup(s)', failed_geo_direct_children, self.failure_response)

        if not valid_geo_direct_children:
            self.log.warning(f"No valid GEO subgroup found. "
                             f"GEO direct children must be groups named 'MODEL_(LOD_TYPE)_grp.")
