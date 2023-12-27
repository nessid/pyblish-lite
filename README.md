# Pyblish Lite

## About This Package

This package is a fork of the [ynput/pyblish-lite](https://github.com/ynput/pyblish-lite) repository, offering a community-driven alternative to pyblish-qml. It's tailored to provide a comprehensive solution for creative workflows in digital content creation tools like Autodesk Maya.

### Key Components and Documentation

- [**Pyblish Lite (`pyblish_lite`)**](./pyblish_lite/package_data/README.md): Contains `pyblish_lite`, a streamlined and optimized version of Pyblish for enhanced performance and usability.
- [**Custom Plugins (`pyblish_plugins`)**](./pyblish_plugins/package_data/README.md): Includes a set of custom plugins designed for specific publishing requirements in creative projects.
- [**Plugins Manager (`pyblish_plugins_manager`)**](./pyblish_plugins_manager/package_data/README.md): Features the `pyblish_plugins_manager` for easy management and integration of plugins.
- [**Pyblish Core (`pyblish_core`)**](./pyblish_core/package_data/README.md): Comprises custom tools and utilities supporting the functionality of plugins and the plugins manager.

Each linked package name leads to a README file with detailed information about specific functionalities, usage instructions, and additional details.

### Pyblish Core Functionality

`pyblish_core` plays a vital role in Pyblish Lite's operation. It handles several key functionalities:

- **Configuration of Logging**: Set up logging for Pyblish Lite to capture and manage log messages.
- **Filepath Tokens Updater**: Initializes `FilepathTokensUpdater` for managing file path tokens, crucial for working with assets and tasks.
- **Dynamic Plugin Registration**: Listens for `pyblish_lite_reset` events, and based on the environment variables `PYBLISH_LITE_ASSET_TYPE` and `PYBLISH_LITE_TASK`, it registers plugins relevant to the current context.

### Purpose of the Fork

The aim of this fork is to provide a robust and flexible publishing framework that is both lightweight and feature-rich. It is designed to address the specific needs of the community and to offer an efficient and customizable publishing solution for various creative production settings.

## Setting Up Pyblish Lite for Maya

The `userSetup.py` file is an essential part of customizing your Maya environment. This script is executed when Maya starts, and it can run any Python commands that do not depend on Maya's functionality. It's particularly useful for setting up plugins, importing libraries, and modifying the system path.

### Creating and Locating `userSetup.py`

1. **Create the `userSetup.py` File**: If it doesn't already exist, you need to create the `userSetup.py` file. This file will contain the commands you want Maya to execute at startup.

2. **File Location**:
   - On Linux and macOS, place the file in `$MAYA_APP_DIR/<version>/scripts`.
   - On Windows, place it in `%MAYA_APP_DIR%/<version>/scripts`.
   
   To find the value of `MAYA_APP_DIR`, run `getenv("MAYA_APP_DIR")` from the Maya Script Editor.

### Configuring `userSetup.py` for Pyblish Lite

Add the following script to your `userSetup.py` to set up Pyblish Lite. This script will ensure that the necessary paths are added to the system path and that the Pyblish modules are loaded correctly:

```python
import os
import sys

# Paths for Pyblish Lite and dependencies
pyblish_lite_path = '/path/to/pyblish_lite'
pyblish_maya_path = '/path/to/pyblish_maya'
pyblish_base_path = '/path/to/pyblish_base'

# Adding paths to system path
sys.path.append(pyblish_lite_path)
sys.path.extend([
    pyblish_maya_path,
    os.path.join(pyblish_maya_path, 'pyblish_maya'),
    os.path.join(pyblish_maya_path, 'pyblish_maya', 'pythonpath'),
    pyblish_base_path
])

# Import and setup Pyblish modules
try:
    import pyblish_lite
    import pyblish_core
    import pyblish_plugins_manager
    import pyblish
    import pyblish_maya
    pyblish_maya.setup()
except ImportError as e:
    import traceback
    print("Pyblish Lite: Could not load integration: %s" % traceback.format_exc())
```

Replace `'/path/to/...'` with the actual paths where your Pyblish Lite and its dependencies are located.

For more detailed information on using the `userSetup.py` file in Maya, you can refer to Autodesk's guides on [Initializing the Maya Python environment](https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Scripting/files/GUID-640C1383-3FB8-410F-AE18-987A812B5914.htm) and [Entering Python commands in Maya](https://download.autodesk.com/us/maya/Maya_2014_GettingStarted/files/Using_Python_in_Maya_Entering_Python_commands.htm).

For more general details on using external Python libraries with Maya, see Autodesk's official guide: [Using external Python libraries with Maya Python](https://help.autodesk.com/view/MAYAUL/).
