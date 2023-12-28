import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya.core import geometry_lib
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class MeshTrianglesValidator(pyblish.api.Validator):
    """Mesh | Triangle faces Validator

    This Pyblish validator plugin ensure that meshes have no triangle faces.

    """
    plugin_id = '84cfab59-4218-4755-b36e-83eb32bd3464'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Triangle faces'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.05

    lod_type = None

    def process(self, context, instance):
        """Main method for processing the current instance

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
        failed_faces = []

        for node in nodes:
            # Count the number of faces in the mesh node
            num_faces = cmds.polyEvaluate(node, face=True)

            # If the mesh has no faces, skip it and log the information
            if num_faces == 0:
                self.log.info(
                    f"Skipping {node} because it does not have any faces."
                )
                continue

            # Define a string 'faces' representing all faces of the current 'node'
            faces = f"{node}.f[*]"

            # Use the geometry_lib.poly_constraint function to find triangles in the mesh faces
            triangles = geometry_lib.poly_constraint(faces,
                                                     t=0x0008,  # Type: Face
                                                     size=1)     # Size: Triangles

            # If triangles are found in the mesh, consider it failed
            if triangles:
                failed_meshes.append(node)
                failed_faces.extend(triangles)

        if failed_meshes:
            # Create 'Select' action subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with triangle faces',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' action subclass for failed faces
            select_failed_faces = actions.create_action_subclass(actions.Select,
                                                                 'triangle face(s)',
                                                                 failed_faces
                                                                 )
            self.actions.append(select_failed_faces)

        # Report the validation result
        validation_result(self, 'mesh(es) with triangle faces', failed_meshes, self.failure_response)
