import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import collection_result
from pyblish_core.name_lib import define_plugin_label


class CameraNodesCollector(pyblish.api.Collector):
    """Collects camera nodes in the Maya scene.

    This Pyblish collector plugin retrieves camera nodes in the current Maya scene:
    - including both camera shapes and their associated transform nodes
    - excluding Maya's default nodes.

    The collected list is added to the Pyblish context as 'camera_nodes' data.
    """
    plugin_id = '02705410-ffb1-429e-b67b-5ce34242f1a0'  # https://www.uuidgenerator.net/version4
    category = 'Nodes'
    name = 'Camera nodes'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):
        """Main method for processing the current context

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # List all camera shapes in the scene
        camera_shapes = cmds.ls(type='camera', long=True)

        # Find the corresponding transform nodes for the camera shapes
        camera_transforms = [cmds.listRelatives(shape, parent=True, fullPath=True)[0] for shape in camera_shapes]

        # Combine camera shapes and their associated transform nodes
        nodes = list(set(camera_shapes).union(camera_transforms))

        # Retrieve nodes to be excluded from validation
        excluded_nodes = context.data['excluded_nodes']

        # Filter out excluded nodes from the collected camera nodes
        nodes = list(set(nodes) - set(excluded_nodes))

        # Store the collected nodes for use in other plugins or actions
        collected_nodes = nodes

        # Store data on the context
        context.data['camera_nodes'] = collected_nodes

        if collected_nodes:
            # Create 'Select' actions subclass for collected nodes
            select_collected_nodes = actions.create_action_subclass(actions.Select,
                                                                    'camera node(s)',
                                                                    collected_nodes
                                                                    )
            self.actions.append(select_collected_nodes)

        # Provide information about the collection in the result
        collection_result(self, 'camera node(s)', collected_nodes)
