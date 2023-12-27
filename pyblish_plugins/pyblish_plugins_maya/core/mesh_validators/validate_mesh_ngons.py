import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya.core import geometry_lib
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


class MeshNgonsValidator(pyblish.api.Validator):
    """Mesh | Ngons Validator

    This Pyblish validator plugin checks for ngons (faces with more than 4 sides).

    NOTE: To address this issue on the meshes, you can use Maya's modeling tool: "Mesh > Cleanup..."

    """
    plugin_id = 'bf7a643e-08b2-42f1-91bf-67f92567066f'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Ngons'

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
        failed_faces = []

        for node in nodes:
            # Check if node is an intermediate object
            intermediate = cmds.getAttr(node + '.intermediateObject')
            if intermediate:
                continue

            # Check if the mesh has any faces
            face_count = cmds.polyEvaluate(node, face=True)
            if face_count == 0:
                continue

            # Get all faces
            faces = f'{node}.f[*]'
            if not cmds.ls(faces):
                continue

            # Filter to n-sided polygon faces (Ngons)
            ngons = geometry_lib.poly_constraint(faces,
                                                 t=0x0008,  # type=face
                                                 size=3) or []  # size=nsided

            if ngons:
                failed_meshes.append(node)
                failed_faces.extend(ngons)

        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with ngons',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' actions subclass for failed faces
            select_failed_faces = actions.create_action_subclass(actions.Select,
                                                                 'ngon(s)',
                                                                 failed_faces
                                                                 )
            self.actions.append(select_failed_faces)

        validation_result(self, 'mesh(es) with ngons', failed_meshes, self.failure_response)
