import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class MeshEmptyValidator(pyblish.api.Validator):
    """Mesh | Empty Validator

    This Pyblish validator plugin checks for meshes with no vertices.

    NOTE: To replicate this issue, delete all faces/polygons then all edges.

    """
    plugin_id = '70fe0770-8299-4d5b-8f8d-8497a49ab11c'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Empty'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.05

    lod_type = None

    def process(self, context, instance):
        """Main method for processing the current instance

        Note:
            This code is adapted from the OpenPype GitHub repository:
            https://github.com/ynput/OpenPype

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of nodes from the context data
        mesh_nodes = context.data['mesh_nodes']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Find the common elements between geo nodes and shape nodes
        nodes = list(set(model_nodes).intersection(mesh_nodes))

        empty_meshes = []

        for node in nodes:
            # Count the number of vertices in the mesh node
            num_vertices = cmds.polyEvaluate(node, vertex=True)

            if num_vertices == 0:
                # If zero vertices are found (empty mesh), add the node to the list of failed nodes
                empty_meshes.append(node)

        if empty_meshes:
            # Create 'Select' actions subclass for empty mesh(es)
            select_empty_meshes = actions.create_action_subclass(actions.Select,
                                                                 'empty mesh(es)',
                                                                 empty_meshes
                                                                 )
            self.actions.append(select_empty_meshes)

        validation_result(self, 'empty mesh(es)', empty_meshes, self.failure_response)
