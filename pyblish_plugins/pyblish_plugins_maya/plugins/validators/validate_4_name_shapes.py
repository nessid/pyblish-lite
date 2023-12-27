import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


class NameShapesValidator(pyblish.api.Validator):
    """Name | Shapes Validator

    This Pyblish validator plugin checks if shapes have the required name:
    [parent transform node's name]+'Shape'.

    """
    plugin_id = '84a45f74-7344-483c-adb9-7914aa3e6ba5'  # https://www.uuidgenerator.net/version4
    category = 'Name'
    name = 'Shapes'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.021

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of nodes from the context data
        shape_nodes = context.data['shape_nodes']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Find the common elements between geo nodes and shape nodes
        nodes = list(set(model_nodes).intersection(shape_nodes))

        # Filter intermediateObjects
        nodes = cmds.ls(nodes, noIntermediate=True, long=True)

        failed_nodes = []  # List to store failed nodes
        renamable_nodes = {}

        # Loop through the shape nodes
        for node in nodes:
            # List relatives of the shape nodes to get their parent transform nodes
            shape_scope = cmds.listRelatives(node, parent=True, fullPath=False)[0]

            if not shape_scope:
                continue

            # Define the expected shape name
            required_shape_name = shape_scope + "Shape"

            # Retrieve the shape short name
            shape_short_name = node.split('|')[-1]

            if shape_short_name != required_shape_name:
                # If the shape has an incorrect name, add it to the failed_nodes list
                failed_nodes.append(node)
                self.log.warning(f"Shape '{shape_short_name}' under '{shape_scope}' has an incorrect name. "
                                 f"Required: '{required_shape_name}'")
                renamable_nodes[node] = required_shape_name

        # Actions
        if failed_nodes:
            # Create 'Select' actions subclass for failed shape(s)
            select_failed_shapes = actions.create_action_subclass(actions.Select,
                                                                  'shape(s) with wrong name',
                                                                  failed_nodes
                                                                  )

            self.actions.append(select_failed_shapes)

        if renamable_nodes:
            # Create 'Rename' actions subclass for failed shape(s)
            rename_failed_nodes = actions.create_action_subclass(actions.Rename,
                                                                 'shape(s) with wrong name',
                                                                 renamable_nodes
                                                                 )
            self.actions.append(rename_failed_nodes)

        validation_result(self, 'shape(s) with wrong name', failed_nodes, self.failure_response)
