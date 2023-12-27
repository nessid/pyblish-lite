import sys
from .app import open_plugins_manager

if __name__ == '__main__':
    app = open_plugins_manager()
    sys.exit(app.exec_())
