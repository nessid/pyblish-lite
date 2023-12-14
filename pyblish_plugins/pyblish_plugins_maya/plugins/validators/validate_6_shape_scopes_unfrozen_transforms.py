import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.results_lib import generate_result_message
from pyblish_core.name_lib import define_plugin_label


class FreezeTransformsOnFailedNodes(pyblish.api.Action):
    """Freeze Transforms On Failed Nodes Action

    This Pyblish action selects components (faces/edges/vertices) that have failed validation.
    It is triggered when a plugin has failed validation or had a warning.

    """
    label = 'Freeze transforms on failed nodes'
    on = 'failedOrWarning'  # Triggered when a plugin has failed validation or had a warning

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The plugin that triggered the action
        """
        # Clear the selection to avoid confusion with current selection.
        cmds.select(clear=True)

        # List the remaining items from plugin.failed_components
        items = cmds.ls(plugin.failed_shape_scopes, long=True)

        # Check if any components were listed
        if items:
            # If failed nodes were listed, freeze transforms
            cmds.makeIdentity(items, apply=True, translate=1, rotate=1, scale=1, normal=0)

        result_msg = generate_result_message('node(s)', items, 'transforms frozen')
        self.log.info(result_msg)


class ShapeScopesUnfrozenTransformsValidator(pyblish.api.Validator):
    """'Shape scopes | Unfrozen transforms' Validator

    This Pyblish validator plugin checks if the transforms that are parents of meshes have frozen transformations.
    If unfrozen transforms are found, they are considered failed nodes.

    """
    plugin_id = 'b872a596-e3ce-4012-b276-ba32ae7601cb'  # https://www.uuidgenerator.net/version4
    category = 'Shape scopes'
    name = 'Unfrozen transforms'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.04

    failed_shape_scopes = []

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of shape_scopes from the context data
        shape_scopes = context.data['shape_scope_nodes']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Find the common elements between geo nodes and shape nodes
        nodes = list(set(model_nodes).intersection(shape_scopes))

        # Retrieve the shape types abbreviation mapping from the context data
        shapes_abbr_mapping = context.data['shapes_abbr_mapping']

        zero_vector = (0.0, 0.0, 0.0)  # Represents a vector with all components set to zero
        identity_vector = (1.0, 1.0, 1.0)  # Represents an identity vector with all components set to one

        for node in nodes:
            # Find the shape node (non-intermediate) associated with the node
            shape_node = cmds.listRelatives(node, shapes=True, fullPath=True, noIntermediate=True)
            shape_node_type = cmds.nodeType(shape_node)

            # Check if the shape node type is in the 'shapes_abbr_mapping'
            if shape_node_type not in shapes_abbr_mapping:
                continue

            # Get the translation values for the current node
            translate_values = cmds.getAttr(node + '.translate')[0]

            # Round each value in the translation to 6 decimal places
            rounded_translate = tuple(round(value, 6) for value in translate_values)

            # Get the rotation values for the current node
            rotate_values = cmds.getAttr(node + '.rotate')[0]

            # Round each value in the rotation to 6 decimal places
            rounded_rotate = tuple(round(value, 6) for value in rotate_values)

            # Get the scale values for the current node
            scale_values = cmds.getAttr(node + '.scale')[0]

            # Round each value in the scale to 6 decimal places
            rounded_scale = tuple(round(value, 6) for value in scale_values)

            # Check if the transformation values match the defaults
            if rounded_translate == zero_vector and rounded_rotate == zero_vector and rounded_scale == identity_vector:
                continue

            self.failed_shape_scopes.append(node)

        if self.failed_shape_scopes:
            # Create 'Select' actions subclass for failed nodes
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'shape scope(s) with unfrozen transforms',
                                                                 self.failed_shape_scopes
                                                                 )
            self.actions.append(select_failed_nodes)

            self.actions.append(FreezeTransformsOnFailedNodes)

        validation_result(self, 'shape scope(s) with unfrozen transform(s)',
                          self.failed_shape_scopes,
                          self.failure_response)
