import pyblish.api
import maya.cmds as cmds
import re
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.strings_handling import define_basename
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class NameModelTransformsValidator(pyblish.api.Validator):
    """Name | Model Transforms Validator

    This Pyblish validator plugin checks if groups have the required name:
        - {basename}_{lod_type}_grp
        - No increment

    Note: Transform nodes include: groups (group_xform, group_scope) and shape_scopes (shapes parents)

    """
    plugin_id = '8b86afa0-9817-4e02-8676-c9516cdf681b'  # https://www.uuidgenerator.net/version4
    category = 'Name'
    name = 'Groups & shapes scopes'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.02

    @staticmethod
    def _define_lod_set_name(lod_type):
        return f"MODEL_{lod_type.upper()}"

    def _update_model_lod_sets(self, lod_types, model_lod_types):
        # Delete existing LOD sets
        for lod_type in lod_types:
            # Name of the set you want to delete (case-insensitive)
            lod_set = self._define_lod_set_name(lod_type)

            # Create a case-insensitive regular expression pattern
            pattern = re.compile(re.escape(lod_set), re.IGNORECASE)

            # List objectSets that match the pattern
            matching_sets = [set_name for set_name in cmds.ls(type="objectSet") if pattern.search(set_name)]

            if matching_sets:
                cmds.delete(matching_sets)

        # Create LOD sets (based on model lod type collected on context data)
        for model_lod_type in model_lod_types:
            lod_set = self._define_lod_set_name(model_lod_type)
            cmds.sets(name=lod_set, empty=True)

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the complete list of available LOD types
        lod_types = context.data['lod_types']

        # Retrieve the MODEL LOD types from the context data
        model_lod_types = context.data['model_lod_types']

        groups = context.data['group_nodes']
        shape_scopes = context.data['shape_scope_nodes']

        # Retrieve the shape types abbreviation mapping from the context data
        shapes_abbr_mapping = context.data['shapes_abbr_mapping']

        group_suffix = context.data['group_suffix']

        # Retrieve the nodes from the instance data
        model_nodes = instance.data['nodes']

        # Update LOD sets
        self._update_model_lod_sets(lod_types, model_lod_types)

        failed_nodes = []
        renamable_nodes = {}

        for node in model_nodes:
            # Only checks for groups and shape scopes names
            if node not in groups and node not in shape_scopes:
                continue

            node_short_name, basename = define_basename(self, context, node)

            # Iterate through each model LOD type
            for model_lod_type in model_lod_types:
                # Define the model LOD group name based on the model LOD type and group suffix
                model_lod_group = f"MODEL_{model_lod_type.upper()}_{group_suffix}"

                # Check if the model LOD group is part of the node's name
                if model_lod_group not in node:
                    continue

                # Define the LOD set name based on the model LOD type
                lod_set = self._define_lod_set_name(model_lod_type)

                # Determine the required suffix based on the model LOD type
                required_suffix = f"_{model_lod_type}"

                # Check if the node is part of the 'groups' or 'shape_scopes'
                if node in groups:
                    # Add group suffix to the required suffix
                    required_suffix += f"_{group_suffix}"
                elif node in shape_scopes:
                    # Find the shape node (non-intermediate) associated with the node
                    shape_node = cmds.listRelatives(node, shapes=True, fullPath=True, noIntermediate=True)
                    shape_node_type = cmds.nodeType(shape_node)

                    # Check if the shape node type is in the 'shapes_abbr_mapping'
                    if shape_node_type in shapes_abbr_mapping:
                        # Add shape abbreviation suffix to the required suffix
                        required_suffix += f"_{shapes_abbr_mapping[shape_node_type]}"

                        # Add the node to the LOD set
                        cmds.sets(node, add=lod_set)

                # Define the required short and long names for the node
                required_short_name = f"{basename}{required_suffix}"
                required_long_name = str(node).replace(node_short_name, required_short_name)

                # Check if the node matches the required long name
                if node == required_long_name:
                    continue

                # Add the node to the list of failed nodes
                failed_nodes.append(node)

                # Check if the required long name already exists
                if cmds.ls(required_long_name):
                    self.log.warning(f"'{required_long_name}' already exists. '{node}' can't be renamed.")
                else:
                    # Add the node to the dictionary of renamable nodes
                    renamable_nodes[node] = required_short_name

        # Append dynamic actions
        if failed_nodes:
            # Create 'Select' actions subclass for failed node(s)
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'node(s) with incorrect name',
                                                                 failed_nodes
                                                                 )
            self.actions.append(select_failed_nodes)

        if renamable_nodes:
            # Create 'Rename' actions subclass for failed node(s)
            rename_failed_nodes = actions.create_action_subclass(actions.Rename,
                                                                 'node(s)',
                                                                 renamable_nodes
                                                                 )
            self.actions.append(rename_failed_nodes)

        # Report the validation results
        validation_result(self, 'node(s) with incorrect name', failed_nodes, self.failure_response)
