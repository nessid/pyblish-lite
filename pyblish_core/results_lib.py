import pyblish.api
from typing import Union, List, Dict, Optional
import re


def generate_result_message(items_type: str,
                            items: Union[str, List, Dict],
                            result_type: str,
                            max_items_logged=10,
                            processed_instance: Optional[str] = None) -> str:
    """
    Generate a result message for processed items.

    :param items_type: (str) The type of items, such as "node(s)" or "component(s)" (use the plural form in parentheses
    when applicable).
    :param items: (list, dict or str) Item(s) that were processed.
    :param result_type: (str) Type of result (e.g., "collected", "validated", "processed").
    :param max_items_logged: (int) Beyond this number, items names won't be logged.
    :param processed_instance: (str, optional) The instance that was processed.

    :return: (str) A message indicating the number of items processed and their names (if between 1 and 5).
    """
    if isinstance(items, str):
        items_nbr = 1
    else:
        items_nbr = len(items)

    # Remove parentheses and their content if there's only one item,
    # otherwise remove all parentheses to make the message plural.
    item_type = re.sub(r'\([^)]*\)' if items_nbr <= 1 else r'[()]', '', items_type)

    # Create a message indicating the number of items
    # Handle the case when there are no items
    items_num = 'No' if items_nbr == 0 else str(items_nbr)
    instance_msg = f"Instance '{processed_instance}' processed -- > " if processed_instance is not None else ''
    validation_msg = f"{instance_msg}{items_num} {item_type} {result_type}"

    if isinstance(items, str):
        validation_msg += f": {items}."
    elif 0 < items_nbr <= max_items_logged:
        # If there are between 1 and max_items_logged collected items, append their names to the message
        validation_msg += f": {', '.join(items)}."
    else:
        # Else just finish the message with a dot
        validation_msg += '.'

    return validation_msg


def handle_item_renaming_result(action_instance,
                                original_item_fullpath: str,
                                renamed_item_fullpath: str,
                                successful_renames: List[str],
                                failed_renames: List[str]):
    """Process and log the results of renaming an item.

    This function handles and reports the results of renaming an item. It distinguishes between successful renames and
    various error cases, such as duplicates, unchanged names, and items with no name except for a suffix.

    :param action_instance: The Pyblish action instance.
    :param original_item_fullpath: The full path of the original item.
    :param renamed_item_fullpath: The full path of the renamed item.
    :param successful_renames: A list of strings containing successfully renamed items.
    :param failed_renames: A list of strings containing items that couldn't be renamed.

    :returns: A tuple containing the updated lists of successful renames and failed renames.
    """
    # Check if the renamed item's name is the same as the original item's name
    if original_item_fullpath == renamed_item_fullpath:
        action_instance.log.warning(f"{renamed_item_fullpath} has not been renamed. Please rename manually.")
        failed_renames.append(renamed_item_fullpath)
    # Check if the renamed item's name starts with an underscore
    elif renamed_item_fullpath.split('|')[-1].startswith('_'):
        action_instance.log.warning(
            f"{renamed_item_fullpath} has no name except for its suffix. Please rename manually.")
        failed_renames.append(renamed_item_fullpath)
    else:
        # If none of the above conditions are met, it's a successful rename.
        successful_renames.append(renamed_item_fullpath)

    # Return the updated lists of successful renames and failed renames
    return successful_renames, failed_renames


def handle_renaming_action_results(action_instance, successful_renames: List[str], failed_renames: List[str]) -> None:
    """Handle and report the results of a renaming action.

    This function reports the results of a renaming action, including nodes that were successfully renamed
    and raises an error for nodes that couldn't be renamed or are having a problematic new name.

    :param action_instance: The Pyblish action instance.
    :param successful_renames: A list of strings containing nodes that were successfully renamed.
    :param failed_renames: A list of strings containing nodes that couldn't be renamed.

    :raises pyblish.api.PyblishError: If there are nodes that couldn't be renamed.
    """
    if successful_renames:
        # Generate and log a message for successfully renamed nodes
        msg = generate_result_message('node(s)', successful_renames, 'successfully renamed')

        # Log an info with the message
        action_instance.log.info(msg)

    if failed_renames:
        # Generate a message for nodes that couldn't be renamed
        msg = generate_result_message('node(s)', failed_renames, 'unsuccessfully renamed')

        # Raise a PyblishError with the error message
        raise pyblish.api.PyblishError(msg)

    if not successful_renames and not failed_renames:
        # Generate a message for nodes that couldn't be renamed
        msg = generate_result_message('node(s)', [], 'renamed')

        # Log a warning with the message
        action_instance.log.warning(msg)
