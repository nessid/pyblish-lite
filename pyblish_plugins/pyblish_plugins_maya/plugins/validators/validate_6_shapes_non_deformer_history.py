import pyblish.api
import maya.mel as mel
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.results_lib import generate_result_message
from pyblish_core.name_lib import define_plugin_label


class DeleteNonDeformerHistory(pyblish.api.Action):
    """Delete Non-Deformer History

    This Pyblish action deletes non-deformer history from nodes that have failed validation or produced warnings.

    """
    label = 'Delete non-deformer history'
    on = 'failedOrWarning'

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The plugin that triggered the action
        """
        # List the remaining items from plugin.failed_nodes
        items = cmds.ls(plugin.failed_nodes, long=True)

        # Check if any nodes were listed
        if items:
            # If failed nodes were listed, delete by type --> Non-deformer history
            cmds.select(items)
            mel.eval('doBakeNonDefHistory( 1, {"prePost" });')
            cmds.select(cl=True)
        else:
            # Otherwise clear the selection to avoid confusion with current selection.
            cmds.select(clear=True)

        result_msg = generate_result_message('node(s)', items, 'non-deformer history deleted')
        self.log.info(result_msg)


class HistoryNonDeformerValidator(pyblish.api.Validator):
    """History | Non-deformer Validator

    This Pyblish validator plugin retrieves non-deformer histories on shape nodes in the Maya scene.

    If any shape nodes are found with construction histories, they are marked as failed nodes.

    """
    plugin_id = '42df672c-ac11-4cc9-8ec1-6435f7f5fcc1'  # https://www.uuidgenerator.net/version4
    category = 'Shapes'
    name = 'History | Non-deformer'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.041

    failed_nodes = []

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve the list of nodes from the context data
        shape_nodes = context.data['shape_nodes']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Find the common elements between geo nodes and shape nodes
        nodes = list(set(model_nodes).intersection(shape_nodes))

        for node in nodes:
            # Iterate through objects and check their construction history
            history_nodes = cmds.listHistory(node)
            # Check if the construction history is not empty
            if not history_nodes:
                continue

            # Check for intermediate node
            intermediate_nodes = cmds.ls(history_nodes, exactType='mesh', intermediateObjects=True)
            if not intermediate_nodes:
                continue

            intermediate_history_nodes = cmds.listHistory(intermediate_nodes, interestLevel=1, pruneDagObjects=True)
            if not intermediate_history_nodes:
                continue

            # If non-empty history is found, append to failed_nodes
            self.failed_nodes.append(node)

        if self.failed_nodes:
            # Create 'Select' actions subclass for failed shape(s)
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'shape(s) with non-deformer history',
                                                                 self.failed_nodes
                                                                 )
            self.actions.append(select_failed_nodes)

            self.actions.append(DeleteNonDeformerHistory)

        validation_result(self, 'node(s) with non-deformer history',
                          self.failed_nodes,
                          self.failure_response)
