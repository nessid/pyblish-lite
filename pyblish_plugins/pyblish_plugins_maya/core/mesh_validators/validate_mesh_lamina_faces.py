import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


class MeshLaminaFacesValidator(pyblish.api.Validator):
    """Mesh | Lamina faces Validator

    Lamina faces are faces that share all of their edges and can lead to rendering artifacts and other issues in 3D models.

    This validator identifies and reports mesh nodes with lamina faces as failed nodes.

    """
    plugin_id = 'aab2c9c1-54da-430a-96ed-dbc0253013e4'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Lamina faces'

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

        failed_meshes = []
        failed_faces = []

        for node in nodes:
            lamina_faces = cmds.polyInfo(node, laminaFaces=True)
            if lamina_faces:
                failed_meshes.append(node)
                failed_faces.extend(lamina_faces)

        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with lamina faces',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' actions subclass for failed faces
            select_failed_faces = actions.create_action_subclass(actions.Select,
                                                                 'lamina face(s)',
                                                                 failed_faces
                                                                 )
            self.actions.append(select_failed_faces)

        # Report the validation result
        validation_result(self, 'mesh(es) with lamina faces', failed_meshes, self.failure_response)
