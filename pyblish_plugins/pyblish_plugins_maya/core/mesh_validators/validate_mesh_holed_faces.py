import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya.core import geometry_lib
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class MeshHoleFacesValidator(pyblish.api.Validator):
    """Mesh | Holed faces Validator

    This Pyblish validator plugin checks for holed faces.

    NOTE: It does not check for holes in mesh (missing face).

    """
    plugin_id = '4023c358-40c0-456e-ba6d-45e41674e393'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Holed faces'

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
            # Get all faces
            faces = f"{node}.f[*]"
            if not cmds.ls(faces):
                continue

            holes = geometry_lib.poly_constraint(faces, mode=3, type=8, holes=1)  # to get holed faces
            if holes:
                failed_meshes.append(node)
                failed_faces.extend(holes)

        # Actions
        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with holed faces',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' actions subclass for failed face(s)
            select_failed_faces = actions.create_action_subclass(actions.Select,
                                                                 'holed face(s)',
                                                                 failed_faces
                                                                 )
            self.actions.append(select_failed_faces)

        validation_result(self, 'mesh(es) with holed faces', failed_meshes, self.failure_response)
