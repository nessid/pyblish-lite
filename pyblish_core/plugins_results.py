import pyblish.api
from pyblish_core.results_lib import generate_result_message
from typing import Union, List, Dict


def collection_result(plugin_instance,
                      collected_item_description: str,
                      collected_items: Union[str, List, Dict],
                      max_items_logged=10,
                      processed_instance=None):
    """Report the results of a collection.

    This function checks for collected nodes and generates a message indicating the number
    of nodes found. If there is one or no collected item, it removes parentheses and their content
    from the `collected_item_type` to make the message singular. If there is only one collected item,
    it appends the item's name to the message.

    :param plugin_instance: The instance of the validator.
    :param collected_item_description: The description of collected item(s), using parentheses for plural form.
    :param collected_items: The collected item(s).
    :param max_items_logged: (int) A threshold value; if the number of failed items is less than or equal to this value,
    they will be logged.
    :param processed_instance: The name of the processed instance.
    """
    collection_msg = generate_result_message(collected_item_description,
                                             collected_items,
                                             'collected',
                                             max_items_logged,
                                             processed_instance)

    plugin_instance.log.info(collection_msg)


def validation_result(plugin_instance,
                      failed_item_description: str,
                      failed_items: Union[str, List, Dict],
                      failure_response: str,
                      max_items_logged=10,
                      processed_instance=None):
    """Report the results of a validation.

    This function checks for failed nodes and generates a validation message indicating the number
    of failed nodes found. If there is only one failed node, it removes parentheses and their content
    from the `failed_node_type` to make the message singular. If there is only one failed node,
    it adds the failed node name to the message.
    Finally, it raises a validation error if failed nodes are found or logs a message if no failed nodes are found.

    :param plugin_instance: The instance of the validator.
    :param failed_item_description: The description of failed items, using parentheses for plural form.
    :param failed_items: The failed item(s).
    :param failure_response: The failure response, either 'fail' or 'warning'.
    :param max_items_logged: (int) A threshold value; if the number of failed items is less than or equal to this value,
    they will be logged.
    :param processed_instance: The name of the processed instance.
    """
    validation_msg = generate_result_message(failed_item_description,
                                             failed_items,
                                             'found',
                                             max_items_logged,
                                             processed_instance)

    if failed_items:
        if failure_response == 'fail':
            raise pyblish.api.ValidationError(validation_msg)
        if failure_response == 'warning':
            plugin_instance.log.warning(validation_msg)
    else:
        # If no failed nodes are found, log an info message
        plugin_instance.log.info(validation_msg)
