import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


class ShapeScopesDoubleShapesValidator(pyblish.api.Validator):
    """'Shape scopes | Double shapes' Validator

    This Pyblish validator plugin checks if the transforms that are parents of meshes have frozen transformations.
    If unfrozen transforms are found, they are considered failed nodes.

    """
    plugin_id = 'b5b2004b-cc54-4774-a313-61b30694280b'  # https://www.uuidgenerator.net/version4
    category = 'Shape scopes'
    name = 'Double shapes'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.04

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of shape_scopes from the context data
        shape_scopes = context.data['shape_scope_nodes']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Retrieve nodes to be excluded from validation (expected to be a list)
        excluded_nodes = context.data['excluded_nodes']

        # Find the common elements between model nodes and shape scopes
        nodes = list(set(model_nodes).intersection(shape_scopes))

        failed_shape_scopes = []

        for node in nodes:
            # Find the shape node (non-intermediate) associated with the node
            shape_nodes = cmds.listRelatives(node, shapes=True, fullPath=True, noIntermediate=True)

            # Filter out the excluded nodes from the collected nodes
            shape_nodes = list(set(shape_nodes) - set(excluded_nodes))

            if len(shape_nodes) > 1:
                failed_shape_scopes.append(node)

        if failed_shape_scopes:
            # Create 'Select' actions subclass for failed nodes
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'shape scope(s) with double shapes',
                                                                 failed_shape_scopes
                                                                 )
            self.actions.append(select_failed_nodes)

        validation_result(self, 'shape scope(s) with double shapes', failed_shape_scopes, self.failure_response)

