import sys
from pathlib import Path
from PySide2 import QtWidgets
from .window import PluginsManagerUI
from pyblish_core.lib import configure_logging

# Configure logging
log = configure_logging(__name__)


class PluginsManagerApp:
    """
    This class represents the application for managing plugins.

    It handles the initialization and management of the QApplication and the main window of the application.
    The class is responsible for creating an instance of QApplication, handling the case where an existing
    QApplication instance is already running, and initializing the main window of the application.

    Attributes:
        app (QtWidgets.QApplication): The application instance.
        window (PluginsManagerUI): The main window of the application, initialized when run() is called.

    Methods:
        run: Initializes and displays the plugin manager UI.
        apply_stylesheet: Loads and applies a stylesheet to the application window.
    """
    def __init__(self):
        self.app = QtWidgets.QApplication.instance()

        if not self.app:
            log.info("Starting new QApplication..")
            self.app = QtWidgets.QApplication(sys.argv)
        else:
            app_org = self.app.organizationName()
            app_name = self.app.applicationName()

            log.info(f"Using existing QApplication: {app_org} {app_name}.")

        self.window = None  # Define the attribute here

    def run(self):
        """
        Initializes and shows the plugin manager UI.
        Returns True if the UI was successfully initialized and shown, False otherwise.
        """
        try:
            self.window = PluginsManagerUI()
            self.apply_stylesheet()
            self.window.show()
            log.info("Plugins Manager opened.")
            return True
        except Exception as e:
            log.error(f"Error occurred while initializing the Plugins Manager: {e}", exc_info=True)
            return False

    def apply_stylesheet(self):
        """
        Function to load and apply the stylesheet from 'app.css' located in the same directory as this file.
        Returns True if the stylesheet is applied successfully, False otherwise.
        """
        try:
            # Get the directory of the current file
            current_dir = Path(__file__).resolve().parent

            # Construct the path to the CSS file
            stylesheet_path = current_dir / "app.css"

            with open(stylesheet_path, 'r') as file:
                stylesheet = file.read()
                self.window.setStyleSheet(stylesheet)
                log.info('Window stylesheet applied successfully.')
                return True
        except FileNotFoundError:
            log.error("The stylesheet file was not found.", exc_info=True)
        except IOError:
            log.error("Error occurred while reading the stylesheet file.", exc_info=True)
        except Exception as e:
            log.error(f"An unexpected error occurred: {e}", exc_info=True)
        return False


def open_plugins_manager():
    """
    Main function to run the Plugins Manager application.
    This function initializes the application and handles any exceptions that occur during its execution.
    It logs an error and exits with a status code of 1 if an exception occurs.
    """
    try:
        # Initialize and run the application
        app = PluginsManagerApp()
        app.run()
    except Exception as e:
        log.error("Error in application: %s", e, exc_info=True)
        sys.exit(1)

    return app
