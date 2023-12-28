import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya.core import geometry_lib
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class MeshZeroEdgeLengthValidator(pyblish.api.Validator):
    """Mesh | Zero edge length Validator

    This Pyblish validator plugin checks that meshes do not contain edges with a length of zero.

    NOTE: This validation can be slow for high-resolution meshes.

    Additional Information:
        This validation is based on Maya's polyCleanup tool for 'Edges with zero length', which can be found at:
        http://help.autodesk.com/view/MAYAUL/2015/ENU/?guid=Mesh__Cleanup

    """
    plugin_id = '7fc1c89b-63d7-4bda-b7bf-30af6835dbc7'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Zero edge length'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.05

    lod_type = None

    __tolerance = 1e-5

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
        failed_edges = []

        for node in nodes:
            num_edges = cmds.polyEvaluate(node, edge=True)

            if num_edges == 0:
                self.log.info(
                    f"Skipping {node} because it does not have any edges."
                )
                continue

            # Get all edges
            edges = f'{node}.e[*]'
            if not cmds.ls(edges):
                continue

            # Filter by constraint on edge length
            zero_edge_length = geometry_lib.poly_constraint(edges,
                                                            t=0x8000,  # type=edge
                                                            length=1,
                                                            lengthbound=(0, self.__tolerance))

            if zero_edge_length:
                failed_meshes.append(node)
                failed_edges.extend(zero_edge_length)

        # Actions
        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with zero edge-length',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)
            # Create 'Select' actions subclass for failed edge(s)
            select_failed_edges = actions.create_action_subclass(actions.Select,
                                                                 'edges(s) with zero length',
                                                                 failed_edges
                                                                 )
            self.actions.append(select_failed_edges)

        validation_result(self, 'mesh(es) with zero edge-length', failed_meshes, self.failure_response)
