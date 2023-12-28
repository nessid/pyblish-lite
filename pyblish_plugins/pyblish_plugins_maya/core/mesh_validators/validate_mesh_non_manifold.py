import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class MeshNonManifoldValidator(pyblish.api.Validator):
    """Mesh | Non-manifold edges/vertices Validator

    This Pyblish validator plugin checks for meshes with non-manifold edges or vertices.

    NOTE : To debug the problem on the meshes you can use Maya's modeling tool: "Mesh > Cleanup..."

    """
    plugin_id = '6bd984ac-174e-4be0-aeae-5018cb9964ff'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Non-manifold edges/vertices'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.05

    lod_type = None

    def process(self, context, instance):
        """Main method for processing the current instance.

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

        failed_meshes = []
        failed_edges = []
        failed_vertices = []

        for node in nodes:
            # Use the 'polyInfo' command to retrieve a list of the node's non-manifold edges
            non_manifold_edges = cmds.polyInfo(node, nonManifoldEdges=True) or []
            failed_edges.extend(non_manifold_edges)

            # Use the 'polyInfo' command to retrieve a list of the node's non-manifold vertices
            non_manifold_vertices = cmds.polyInfo(node, nonManifoldVertices=True) or []
            failed_vertices.extend(non_manifold_vertices)

            # Check if there are no non-manifold vertices and no non-manifold edges in the node
            if non_manifold_vertices or non_manifold_edges:
                # Add the current 'node' to the list of failed meshes
                failed_meshes.append(node)

        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'non-manifold meshes',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

        if failed_edges:
            # Create 'Select' actions subclass for failed edges
            select_failed_edges = actions.create_action_subclass(actions.Select,
                                                                 'non-manifold edges',
                                                                 failed_edges
                                                                 )
            self.actions.append(select_failed_edges)

        if failed_vertices:
            # Create 'Select' actions subclass for failed vertices
            select_failed_vertices = actions.create_action_subclass(actions.Select,
                                                                    'non-manifold vertices',
                                                                    failed_vertices
                                                                    )
            self.actions.append(select_failed_vertices)

        validation_result(self, 'non-manifold mesh(es)', failed_meshes, self.failure_response)
