import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class GhostShapesValidator(pyblish.api.Validator):
    """Ghost Shapes Validator

     This Pyblish validator plugin checks for ghost shapes in a Maya scene.
     Ghost shapes are intermediate shapes that may not be needed in the final rendering or animation.
     Identifying and removing them can help optimize the scene.

     The plugin searches for intermediate shapes and checks if they have any history.
     If a ghost shape is identified, it is considered a failed node and can be selected or deleted using the associated actions.

     """
    plugin_id = '30267857-71fe-4770-ae5f-a17d3b2e8c62'  # https://www.uuidgenerator.net/version4
    category = 'Clean'
    name = 'Ghost shapes'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.01

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

        failed_nodes = []

        for node in nodes:
            # Check if node is an intermediate object
            intermediate = cmds.getAttr(node + '.intermediateObject')
            if not intermediate:
                continue

            # Check for node outputs
            outputs = cmds.listConnections(node, source=False, destination=True)

            # Exclude any nodeGraphEditorInfo nodes from the outputs list
            if outputs:
                nodegraph_nodes = cmds.ls(type='nodeGraphEditorInfo')
                for nn in nodegraph_nodes:
                    if nn in outputs:
                        outputs.remove(nn)

            # If there are still outputs, it's not a ghost shape
            if outputs:
                continue

            # If there are no outputs, it's a ghost shape (failed node)
            failed_nodes.append(node)

        # Actions
        if failed_nodes:
            # Create 'Select' actions subclass for failed node(s)
            select_ghost_shapes = actions.create_action_subclass(actions.Select,
                                                                 'ghost shape(s)',
                                                                 failed_nodes
                                                                 )
            self.actions.append(select_ghost_shapes)

            # Create 'Delete' actions subclass for failed node(s)
            delete_ghost_shapes = actions.create_action_subclass(actions.Delete,
                                                                 'ghost shape(s)',
                                                                 failed_nodes
                                                                 )
            self.actions.append(delete_ghost_shapes)

        validation_result(self, 'ghost shape(s)', failed_nodes, self.failure_response)
