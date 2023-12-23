# Pyblish Lite

[Using external Python libraries with Maya Python](https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-C24973A1-F6BF-4614-BC3A-9F1A51D78F4C)

userSetup content:
```
import os
import sys


sys.path.append('/home/nadia.essid/data/packages/nessid/pyblish_lite')  # Path to pyblish_lite


pyblish_maya_path = '/z/apps/tools/external/pyblish_maya/2.1.10/python'
sys.path.append(pyblish_maya_path)
sys.path.append(os.path.join(pyblish_maya_path, 'pyblish_maya'))
sys.path.append(os.path.join(pyblish_maya_path, 'pyblish_maya', 'pythonpath'))


pyblish_base_path = '/z/apps/tools/external/pyblish_base/1.8.11/python'
sys.path.append(pyblish_base_path)

import pyblish_lite
import pyblish_core
import pyblish_plugins_manager
import pyblish



try:
    __import__("pyblish.api")
    __import__("pyblish_maya")

except ImportError as e:
    import traceback

    print("pyblish-maya: Could not load integration: %s"
          % traceback.format_exc())
else:
    import pyblish_maya

    pyblish_maya.setup()
```