
try:
    __import__("pyblish_core")

except ImportError as e:
    import traceback

    print("pyblish_lite: Could not load integration: %s"
          % traceback.format_exc())
