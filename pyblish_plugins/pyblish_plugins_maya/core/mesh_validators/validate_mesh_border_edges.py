import pyblish.api
import maya.cmds as cmds
from maya_lib import geometry_lib
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.name_lib import define_plugin_label


def create_action_subclass(superclass, _state: str, _failed_nodes):
    class Subclass(superclass):
        state = _state
        failed_nodes = _failed_nodes

        label = f"Display borders | {state.upper()}"

    return Subclass


class DisplayBordersSwitch(pyblish.api.Action):
    """Display Borders Switch Action

    This Pyblish action switches borders display on failed nodes.
    """
    state = None
    label = None
    on = 'all'
    failed_nodes = None

    def process(self) -> None:
        # List the remaining items from plugin.failed_nodes
        items = cmds.ls(self.failed_nodes, long=True)

        # Select the items in the Maya scene to operate on
        cmds.select(items, replace=True)

        for item in items:
            # Create the attribute name for controlling display borders
            display_attr = f'{item}.displayBorders'

            # Set the displayBorders attribute to 1 if active is True, otherwise set it to 0
            cmds.setAttr(display_attr, 1 if self.state == 'on' else 0)

        # Open edge width window
        cmds.ChangeEdgeWidth()

        # Log an informational message indicating borders display state
        self.log.info(f"Borders display turned {self.state}")


class MeshBorderEdgesValidator(pyblish.api.Validator):
    """Mesh | Border Edges Validator

    This Pyblish validator plugin checks for mesh nodes with open or border edges.

    """
    plugin_id = 'a9b02145-4637-40f9-a387-c041d4f2fe90'  # https://www.uuidgenerator.net/version4
    category = 'Mesh'
    name = 'Border Edges'

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

        failed_nodes, failed_components = [], []

        for node in mesh_nodes:

            num_edges = cmds.polyEvaluate(node, edge=True)

            if num_edges == 0:
                self.log.info(f"Skipping {node} because it does not have any edges.")
                continue

            # Get all edges
            edges = f'{node}.e[*]'
            if cmds.ls(edges):
                # Check for open edges using Maya's PolySelectConstraint
                open_edges = geometry_lib.poly_constraint(edges, border=1, type=0x8000, where=1, mode=2)

                if open_edges:
                    failed_nodes.append(node)
                    failed_components.extend(open_edges)

        if failed_nodes:
            # Create 'Select' actions subclass for failed meshes
            select_failed_meshes = actions.create_action_subclass(actions.Select,
                                                                  'mesh(es) with open edges',
                                                                  failed_nodes
                                                                  )
            self.actions.append(select_failed_meshes)

            # Create 'Select' actions subclass for open edges
            select_open_edges = actions.create_action_subclass(actions.Select,
                                                               'open edges',
                                                               failed_components
                                                               )
            self.actions.append(select_open_edges)

            display_borders_on = create_action_subclass(DisplayBordersSwitch, 'on', failed_nodes)
            display_borders_off = create_action_subclass(DisplayBordersSwitch, 'off', failed_nodes)

            self.actions.extend([display_borders_on, display_borders_off])

        validation_result(self, 'mesh(es) with open edges', failed_nodes, self.failure_response)
