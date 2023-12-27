"""
@package: maya_lib.context_lib
@module: context_lib.py
@synopsis: Functions for context management in Maya
@description: This module provides functions for context management in Maya.
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
from maya.api import OpenMaya
import contextlib


@contextlib.contextmanager
def no_undo(flush=False):
    """Disable the undo queue during the context

    Arguments:
        flush (bool): When True the undo queue will be emptied when returning
            from the context, losing all undo history. Defaults to False.

    Note:
        This code is adapted from the OpenPype GitHub repository:
        https://github.com/ynput/OpenPype
    """
    original = cmds.undoInfo(query=True, state=True)
    keyword = 'state' if flush else 'stateWithoutFlush'

    try:
        cmds.undoInfo(**{keyword: False})
        yield
    finally:
        cmds.undoInfo(**{keyword: original})


@contextlib.contextmanager
def tool(context):
    """Set a tool context during the context manager.

    Note:
        This code is adapted from the OpenPype GitHub repository:
        https://github.com/ynput/OpenPype
    """
    original = cmds.currentCtx()
    try:
        cmds.setToolTo(context)
        yield
    finally:
        cmds.setToolTo(original)


@contextlib.contextmanager
def maintained_selection_api():
    """Maintain selection using the Maya Python API.

    Warning: This is *not* added to the undo stack.

    Note:
        This code is adapted from the OpenPype GitHub repository:
        https://github.com/ynput/OpenPype
    """
    original = OpenMaya.MGlobal.getActiveSelectionList()
    try:
        yield
    finally:
        OpenMaya.MGlobal.setActiveSelectionList(original)


@contextlib.contextmanager
def reset_poly_select_constraint(reset=True):
    """Context during which the given polyConstraint settings are disabled.

    The original settings are restored after the context.

    Note:
        This code is adapted from the OpenPype GitHub repository:
        https://github.com/ynput/OpenPype
    """

    original = cmds.polySelectConstraint(query=True, stateString=True)

    try:
        if reset:
            # Ensure command is available in mel
            # This can happen when running standalone
            if not mel.eval("exists resetPolySelectConstraint"):
                mel.eval("source polygonConstraint")

            # Reset all parameters
            mel.eval("resetPolySelectConstraint;")
        cmds.polySelectConstraint(disable=True)
        yield
    finally:
        mel.eval(original)
