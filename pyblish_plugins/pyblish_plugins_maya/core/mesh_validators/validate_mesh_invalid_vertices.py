import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.results_lib import generate_result_message
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class CleanInvalidVertices(pyblish.api.Action):
    """Clean Invalid Vertices

    This Pyblish action clean invalid vertices on nodes that have failed validation.
    It is triggered when a plugin has failed validation or had a warning.

    """
    label = "Clean invalid vertices"
    on = "failedOrWarning"  # The plug-in has been processed, and failed or had a warning

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The plugin that triggered the action
        """
        # List the remaining items from plugin.failed_nodes
        items = cmds.ls(plugin.failed_nodes, long=True)

        # Check if any nodes were listed
        if items:
            # If failed nodes were listed, clean vertices
            for node in items:
                cmds.polyClean(node, cleanVertices=True)
        else:
            # Otherwise clear the selection to avoid confusion with current selection.
            cmds.select(clear=True)

        result_msg = generate_result_message('node(s)', items, 'with invalid vertices cleaned')
        self.log.info(result_msg)


class MeshInvalidVerticesValidator(pyblish.api.Validator):
    """Mesh | Invalid Vertices Validator

    This Pyblish validator plugin checks for invalid geometry with vertices that have no edges or faces connected to them.

    """
    plugin_id = '88f7005a-6e9b-46a9-9f1f-cf29e148b569'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Invalid Vertices'

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
        failed_vertices = []

        for node in nodes:
            # Check if the mesh has invalid vertices
            invalid_vertices = cmds.polyInfo(node, invalidVertices=True)
            if invalid_vertices:
                failed_meshes.append(node)
                failed_vertices.extend(invalid_vertices)

        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with invalid vertices',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' actions subclass for invalid vertices
            select_failed_vertices = actions.create_action_subclass(actions.Select,
                                                                    'invalid vertices',
                                                                    failed_vertices
                                                                    )
            self.actions.append(select_failed_vertices)

            self.actions.append(CleanInvalidVertices)

        validation_result(self, 'mesh(es) with invalid vertices', failed_meshes, self.failure_response)
