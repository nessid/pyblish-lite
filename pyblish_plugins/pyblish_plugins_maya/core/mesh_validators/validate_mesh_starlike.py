import pyblish.api
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


class StarLikeVerticesValidator(pyblish.api.Validator):
    """Mesh | Starlike vertices Validator

    This Pyblish validator plugins checks for starlike vertices in mesh nodes.

    NOTE: a starlike vertex is defined as a vertex with more than 5 edges connected to it.

    """
    plugin_id = '4593cf72-2fc0-449c-8e42-20e0a47cf378'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Starlike vertices'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.05

    lod_type = None

    @staticmethod
    def _find_vertices_with_more_than_5_edges(mesh_name: str) -> list[str]:
        """Find vertices in a mesh with more than 5 connected edges.

        This function uses the Maya API to find vertices in a mesh that have more than 5 connected edges.
        It returns a list of the vertices that meet this condition.

        :param mesh_name: Name of the mesh node
        :return: List of vertices with more than 5 connected edges
        """
        # Access the mesh node
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(mesh_name)
        dag_path = OpenMaya.MDagPath()
        selection_list.getDagPath(0, dag_path)

        vertices: list[str] = []

        # Access mesh data using iterator
        vertex_iterator = OpenMaya.MItMeshVertex(dag_path)
        while not vertex_iterator.isDone():
            vertex_index = vertex_iterator.index()

            # Get connected edges
            connected_edges = OpenMaya.MIntArray()
            vertex_iterator.getConnectedEdges(connected_edges)

            # Check if the vertex has more than 5 edges
            if connected_edges.length() > 5:
                vertex = f"{mesh_name}.vtx[{vertex_index}]"
                vertex = cmds.ls(vertex, long=True)
                if vertex:
                    vertices.extend(vertex)

            vertex_iterator.next()

        return vertices

    def process(self, context, instance):
        """Main method for processing the current instance.

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
            vertices = self._find_vertices_with_more_than_5_edges(node)
            if vertices:
                failed_meshes.append(node)
                failed_vertices.extend(vertices)

        # Actions
        if failed_meshes:
            # Create 'Select' actions subclass for failed mesh(es)
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) starlike vertices',
                                                                  failed_meshes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' actions subclass for failed vertices
            select_failed_vertices = actions.create_action_subclass(actions.Select,
                                                                    'starlike vertices',
                                                                    failed_vertices
                                                                    )
            self.actions.append(select_failed_vertices)

        # Report the validation result
        validation_result(self, 'mesh(es) starlike vertices', failed_meshes, self.failure_response)
