"""
@package: maya_lib.geometry_lib
@module: geometry_lib.py
@synopsis: Functions to perform operations on geometry in Maya
@description: This module provides functions to perform operations on geometry in Maya
"""

__author__ = "Nadia ESSID"
__authors__ = ["Nadia ESSID"]
__contact__ = "nessid@zag.com"
__copyright__ = "Copyright 2023, ZAG Studios, All rights reserved."
__date__ = "2023/10/27"
__deprecated__ = False
__email__ = "nessid@zag.com"
__maintainer__ = "Nadia ESSID"
__status__ = "Beta"

# External imports
from maya import cmds, mel
from pyblish_plugins.pyblish_plugins_maya.core.context_lib import (
    no_undo,
    tool,
    maintained_selection_api,
    reset_poly_select_constraint
)


def poly_constraint(components, *args, **kwargs):
    """Return the list of *components* with the constraints applied.

    A wrapper around Maya's `polySelectConstraint` to retrieve its results as
    a list without altering selections. For a list of possible constraints
    see `maya.cmds.polySelectConstraint` documentation.

    Arguments:
        components (list): List of components of polygon meshes

    Returns:
        list: The list of components filtered by the given constraints.

    Note:
        This code is adapted from the OpenPype GitHub repository:
        https://github.com/ynput/OpenPype
    """

    kwargs.pop('mode', None)

    with no_undo(flush=False):
        # Reverting selection to the original selection using
        # `maya.cmds.select` can be slow in rare cases where previously
        # `maya.cmds.polySelectConstraint` had set constrain to "All and Next"
        # and the "Random" setting was activated. To work around this we
        # revert to the original selection using the Maya API. This is safe
        # since we're not generating any undo change anyway.
        with tool("selectSuperContext"):
            # Selection can be very slow when in a manipulator mode.
            # So we force the selection context which is fast.
            with maintained_selection_api():
                # Apply constraint using mode=2 (current and next) so
                # it applies to the selection made before it; because just
                # a `maya.cmds.select()` call will not trigger the constraint.
                with reset_poly_select_constraint():
                    cmds.select(components, r=1, noExpand=True)
                    cmds.polySelectConstraint(*args, mode=2, **kwargs)
                    result = cmds.ls(selection=True)
                    cmds.select(clear=True)
                    return result
