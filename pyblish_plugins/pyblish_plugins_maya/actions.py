import pyblish.api
import maya.cmds as cmds
import re
from pyblish_core.plugins_utilities.results_lib import generate_result_message
from pyblish_core.plugins_utilities.results_lib import handle_item_renaming_result
from pyblish_core.plugins_utilities.results_lib import handle_renaming_action_results


def create_action_subclass(superclass, _items_type: str, _items: list or dict, _on='all'):
    class Subclass(superclass):
        items_type = _items_type
        items_list = list(_items)
        items = _items

        items_nbr = len(items_list)
        items_type_format = re.sub(r'\([^)]*\)' if items_nbr <= 1 else r'[()]', '', items_type)

        label = f"{superclass.__name__} {items_type_format}"

        on = _on

    Subclass.__name__ = f"{superclass.__name__} {_items_type}"
    Subclass.__doc__ = superclass.__doc__
    return Subclass


class Select(pyblish.api.Action):
    """Select Items

    This Pyblish action selects items based on the provided list.

    """
    items_type = None
    items_list = None

    label = None
    on = None  # 'all' or 'failedOrWarning' or ...
    icon = 'mail-reply-all (alias)'

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The plugin that triggered the action
        """
        if self.items_list is None:
            self.log.warning(f"No {self.items_type} list provided. Action cannot be executed.")
            return

        # List the items based on the provided list
        items = cmds.ls(self.items_list, long=True)

        # Check if any components were listed
        if items:
            # If components were listed, select them.
            cmds.select(items, replace=True, noExpand=True)
        else:
            # Otherwise clear the selection to avoid confusion with the current selection.
            cmds.select(clear=True)

        result_msg = generate_result_message(self.items_type, items, 'selected')
        self.log.info(result_msg)


class Delete(pyblish.api.Action):
    """Delete Items

    This Pyblish action deletes items based on the provided list.

    """
    items_type = None
    items_list = None

    label = None
    on = None  # 'all' or 'failedOrWarning' or ...
    icon = 'trash'

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The plugin that triggered the action
        """
        if self.items_list is None:
            self.log.warning(f"No {self.items_type} list provided. Action cannot be executed.")
            return

        # List the items based on the provided list
        items = cmds.ls(self.items_list, long=True)

        # Check if any nodes were listed
        if items:
            # If failed nodes were listed, delete them.
            cmds.delete(items)
        else:
            # Otherwise clear the selection to avoid confusion with current selection.
            cmds.select(clear=True)

        result_msg = generate_result_message(self.items_type, items, 'deleted')
        self.log.info(result_msg)


class Rename(pyblish.api.Action):
    """Select Invalid Root Nodes Action

    This Pyblish action renames items based on the provided list.

    """
    items_type = None
    items_list = None
    items = None

    label = None
    on = None  # 'all' or 'failedOrWarning' or ...
    icon = "mail-reply-all (alias)"

    def process(self, plugin):
        """Main method for processing the action

        :param plugin: The plugin that triggered the action
        """
        # Initialize two empty lists to keep track of successful and failed renames.
        successful_renames, failed_renames = [], []

        renamable_nodes = self.items

        # Sort the list of nodes by their length in descending order.
        # This ensures that longer node names appear before shorter ones, helping
        # to select nodes with longer, more specific names that match the pattern.
        nodes = sorted(renamable_nodes, key=len, reverse=True)

        for node in nodes:
            new_name = renamable_nodes[node]
            if cmds.ls(node):
                # Rename the node and store its name in a variable
                node_renamed_short = cmds.rename(node, new_name)
                node_renamed_long = str(node).replace(str(node).split('|')[-1], node_renamed_short)
                self.log.info(f"'{node}' renamed '{new_name}'")

                # Process the renaming result for the current node
                # and update the lists of successful and failed renames.
                successful_renames, failed_renames = handle_item_renaming_result(self,
                                                                                 str(node),
                                                                                 node_renamed_long,
                                                                                 successful_renames,
                                                                                 failed_renames)

        # After processing all renaming results, handle and log the overall results for the action.
        handle_renaming_action_results(self,
                                       successful_renames,
                                       failed_renames)
