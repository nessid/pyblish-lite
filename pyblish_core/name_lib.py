import re


def find_pattern(input_string: str, pattern: str) -> list[str]:
    """Check if a given input string contains multiple occurrences of a specified pattern, case-insensitively.

    :param input_string: (str) The input string to search for patterns within.
    :param pattern: (str) The pattern to search for in the input string.

    This function determines if the input string contains multiple occurrences of the given pattern
    (with optional numbers) in a case-insensitive manner.

    :return: (List[str]) A list of matching patterns found in the input string.
    """
    # Create a regular expression pattern to match 'pattern' with underscores and optional numbers
    regex_pattern = re.compile(rf'(?:^|_){re.escape(pattern)}\d*(?:_|$)', re.IGNORECASE)

    # Use the regular expression pattern to find all matches
    matches = regex_pattern.findall(input_string)

    # Remove underscores from the matches
    matches = [pattern.strip('_') for pattern in matches]

    return matches


def remove_pattern(input_string: str, pattern: str) -> str:
    """Remove a specific pattern from an input string, case-insensitively.

    :param input_string: (str) The input string.
    :param pattern: (str) The pattern to be removed.

    This function searches for all occurrences of the given pattern in the input string
    prefixed or suffixed by underscores and removes them in a case-insensitive manner.

    :return: (str) The input string with the pattern removed.
    """
    pattern = rf'{pattern}\d*'

    # Define the regular expression pattern with the IGNORECASE flag
    regex_pattern = f'_{pattern}|{pattern}_'

    # Use re.sub with re.IGNORECASE to remove matching patterns case-insensitively
    output_string = re.sub(regex_pattern, '', input_string, flags=re.IGNORECASE)

    # Return the modified output string.
    return output_string


def contains_letters(input_string):
    """Check if the input string contains any letters (alphabetic characters).

    :param input_string: (str) The input string to check.

    This function checks if the input string contains any letters (alphabetic characters).

    :return: (bool) True if the input string contains letters, False if it only contains digits or special characters.
    """
    # Use the isalpha() method to check if the string contains letters
    return any(char.isalpha() for char in input_string) if input_string else False


def define_basename(plugin_instance, context, node: str):
    """ Define the base name for a given node, considering reserved patterns and default values.

    The function defines the base name for a given node by taking the node's short name, removing reserved patterns,
    and handling special cases where the base name is empty or in the list of reserved patterns.
    If the base name is empty or reserved, it falls back to the default base name and logs a warning.

    :param plugin_instance: (object) An instance of the plugin.
    :param context: The context containing reserved patterns and default values data.
    :param node: (str) The node's name for which the base name is being defined.

    :return tuple: A tuple containing the original node name and the computed base name.
    """
    # Retrieve the reserved_patterns from the context data
    reserved_patterns = context.data['reserved_patterns']

    # Extract the short name of the node
    node_short_name = str(node).split('|')[-1]

    # Initialize the basename with the short name
    basename = node_short_name

    # Remove reserved patterns from the basename
    for reserved_pattern in reserved_patterns:
        basename = remove_pattern(basename, reserved_pattern)

    # Remove duplicate underscores
    basename = re.sub(r'_+', '_', basename)

    # Remove leading and trailing underscores
    basename = basename.strip('_')

    # Check if the final basename is empty or in reserved patterns
    if not basename or basename in reserved_patterns:
        # Fallback to the default basename and log a warning
        plugin_instance.log.warning(f"'{node}' has no valid basename.")

    return node_short_name, basename


def define_plugin_label(category: str, name: str):
    """
    Concatenates the given category and name to define a plugin label.

    Args:
    :param category: (str) The category of the plugin.
    :param name: (str) The name of the plugin.

    Returns:
    str: A string combining the category and name to form the plugin's label.
    """
    # Generates a label for a plugin using its category and name
    return category + ' | ' + name
