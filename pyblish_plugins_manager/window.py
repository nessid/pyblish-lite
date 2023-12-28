from typing import Dict, Any, Union
import os
import json
import pyblish.api
from pyblish_core.plugins_data_generator import PluginsDataGenerator
from PySide2 import QtGui
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QSplitter, QHBoxLayout, QVBoxLayout
from pyblish_core.lib import configure_logging

# Configure logging
log = configure_logging(__name__)


class PluginsManagerUI(QtWidgets.QDialog):
    """ A dialog for managing Pyblish plugins.

    This user interface allows users to view and manage settings for various plugins
    used in the Pyblish pipeline. It provides options to select asset types and
    tasks, and displays plugins relevant to the selected context. Users can save custom
    settings, reset to last saved settings, and export the plugins data to a JSON file.

    The UI is divided into several sections:
    - A selection area for choosing the asset type and task.
    - A tree widget that lists all the plugins applicable to the selected task, along with
      options to modify their behavior.
    - A tab widget that can display additional details or settings related to the plugins.
    - Advanced options for additional control over the plugins.
    """

    WINDOW_TITLE = "Pyblish | Plugins Manager"
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 850

    # UI Colors for different plugin states
    DEFAULT_COLOR = 'lightGray'
    LOCKED_COLOR = 'gray'
    OVERRIDEN_COLOR = 'orange'

    PLUGINS_SETTINGS_ENV_VAR = "PYBLISH_PLUGINS_SETTINGS_BY_TASKS_JSON"
    ASSET_TASKS_MAPPING_ENV_VAR = "PYBLISH_ASSET_TASKS_MAPPING_JSON"

    DETAILS_TAB_INDEX = -1  # Placeholder for the index of the details tab

    def __init__(self, parent=None):
        super(PluginsManagerUI, self).__init__(parent)

        # Set window title and size
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Check and retrieve environment variables
        self.check_env_variable(self.PLUGINS_SETTINGS_ENV_VAR)
        self.check_env_variable(self.ASSET_TASKS_MAPPING_ENV_VAR)

        # Retrieve environment variables' values
        self.plugins_settings_file = os.getenv(self.PLUGINS_SETTINGS_ENV_VAR)
        self.asset_tasks_mapping_file = os.getenv(self.ASSET_TASKS_MAPPING_ENV_VAR)

        # Read jsons from the environment variable
        self.plugins_settings = self.read_json_file(self.plugins_settings_file)
        self.assetTasksMapping = self.read_json_file(self.asset_tasks_mapping_file)

        # UI Components: Tree Widget for displaying plugins
        self.pluginTreeWidget = CustomTreeWidget()

        # UI Components: Labels and Combo Boxes for asset type and task selection
        self.assetTypeLabel = QtWidgets.QLabel("Asset Type")
        self.assetTypeComboBox = QtWidgets.QComboBox()
        self.taskLabel = QtWidgets.QLabel("Task")
        self.taskComboBox = QtWidgets.QComboBox()

        # Tab Widget for additional details or settings
        self.tabWidget = QtWidgets.QTabWidget()

        # UI Components: Buttons for various actions (initialized in `create_widgets`).
        self.saveButton = None
        self.resetButton = None
        self.dumpPluginsDataJsonButton = None

        # Layout management: Splitter for resizing UI sections
        self.splitter = None

        # Advanced UI options
        self.advancedOptionsCheckbox = QtWidgets.QCheckBox("Advanced")
        self.advancedGroupBox = QtWidgets.QGroupBox()

        # Plugin data generator and collections for plugin data
        self.generator = PluginsDataGenerator()
        self.pluginsData = self.generator.collect_plugins_data()
        self.plugins_packages = {}
        self.plugins_types = {}
        self.plugins_categories = {}

        # Method calls to set up UI
        self.create_widgets()
        self.create_layout()
        self.populate_plugins()
        self.create_connections()

        # Load initial task settings and update UI
        initial_asset_type = self.assetTypeComboBox.currentText()
        initial_task = self.taskComboBox.currentText()
        self.currentTask = initial_task
        self.update_ui_with_task_settings(initial_asset_type, initial_task)

    @staticmethod
    def check_env_variable(var_name: str):
        """
        Check the existence of an environment variable.

        :param var_name: (str) The name of the environment variable.
        """
        if not os.getenv(var_name):
            raise EnvironmentError(f"Environment variable '{var_name}' is not set.")

    def create_widgets(self):
        """ Creates and configures the widgets used in the Plugins Manager UI.

        This method initializes and configures various widgets such as combo boxes,
        buttons, and the plugin tree widget. It sets up the UI components including
        the asset type and task dropdowns, save and reset buttons, advanced options,
        and the main tree widget that lists plugins.

        The dropdown widths are adjusted to fit the content, and the tree widget
        is configured with appropriate headers and initial column widths.
        """

        def adjust_combobox_width(combobox: QtWidgets.QComboBox):
            """
            Adjusts the width of a combo box to fit the longest item, taking into account
            the style metrics of the combo box for padding and button size.

            :param combobox: The combo box to adjust.
            """
            longest_text = max([combobox.itemText(i) for i in range(combobox.count())], key=len)
            font_metrics = combobox.fontMetrics()
            text_width = font_metrics.horizontalAdvance(longest_text)

            # Calculate extra space for the dropdown button and padding
            extra_space = combobox.style().pixelMetric(QtWidgets.QStyle.PM_ComboBoxFrameWidth)
            button_width = combobox.style().pixelMetric(QtWidgets.QStyle.PM_ButtonIconSize)
            padding = combobox.style().pixelMetric(QtWidgets.QStyle.PM_FocusFrameHMargin) + 1

            # Set the minimum width based on text width and calculated extra space
            combobox.setMinimumWidth(text_width + button_width + 2 * (extra_space + padding))

        # Populate the dropdown menus
        self.assetTypeComboBox.addItems(self.assetTasksMapping.keys())
        self.taskComboBox.addItems(self.assetTasksMapping.get(self.assetTypeComboBox.currentText(), []))

        # Adjust widths to fit content
        adjust_combobox_width(self.assetTypeComboBox)
        adjust_combobox_width(self.taskComboBox)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setToolTip("Save the current settings")

        self.resetButton = QtWidgets.QPushButton("Reset")
        self.resetButton.setToolTip("Reset settings to the last saved state")

        # Checkbox for toggling advanced options
        self.advancedOptionsCheckbox.setChecked(False)

        # Advanced section group box (not checkable)
        self.advancedGroupBox.setVisible(False)  # Start hidden

        # Advanced option: Dump JSON button
        self.dumpPluginsDataJsonButton = QtWidgets.QPushButton("Dump plugins data JSON")
        self.dumpPluginsDataJsonButton.setToolTip("Dump plugins data (collected from PYBLISH_PLUGINS_FOLDERS) "
                                                  "to JSON in /tmp folder")

        self.pluginTreeWidget.setHeaderLabels(["Module Path", "Active", "Failure Response"])
        self.pluginTreeWidget.setColumnWidth(0, 350)
        self.pluginTreeWidget.setColumnWidth(1, 50)
        self.pluginTreeWidget.setColumnWidth(2, 100)  # Adjust the width as needed
        # self.pluginTreeWidget.setAlternatingRowColors(True)

    def create_layout(self):
        """ Sets up the layout for the Plugins Manager UI.

        This method arranges the UI components created in `create_widgets` into a coherent layout.
        """
        # Layout for asset type and task
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(self.assetTypeLabel)
        selection_layout.addWidget(self.assetTypeComboBox)
        selection_layout.addWidget(self.taskLabel)
        selection_layout.addWidget(self.taskComboBox)
        selection_layout.addStretch(1)  # Push everything to the left

        # Layout for buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.resetButton)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.saveButton)

        # Create the main splitter layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.pluginTreeWidget)
        self.splitter.addWidget(self.tabWidget)
        self.splitter.setSizes([.6 * self.width(), .4 * self.width()])

        # Combine everything into the main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(selection_layout)  # Add the combined asset type and task layout
        main_layout.addWidget(self.splitter)
        main_layout.addLayout(buttons_layout)

        # Layout for the advanced options toggle
        advanced_toggle_layout = QHBoxLayout()
        advanced_toggle_layout.addWidget(self.advancedOptionsCheckbox)
        advanced_toggle_layout.addStretch(1)  # Push checkbox to the left

        # Adding the button to the advanced group box
        advanced_layout = QtWidgets.QVBoxLayout(self.advancedGroupBox)

        # Create a horizontal layout for the button
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.dumpPluginsDataJsonButton)
        button_layout.addStretch(1)  # Add stretch to the right of the button

        # Add the horizontal layout to the advanced layout
        advanced_layout.addLayout(button_layout)
        advanced_layout.addStretch(1)  # This will push everything to the top

        # Add advanced toggle and section to the main layout
        main_layout.addLayout(advanced_toggle_layout)
        main_layout.addWidget(self.advancedGroupBox)

        # Set the main layout for the dialog
        self.setLayout(main_layout)

    def create_or_get_tree_item(self, parent: QtWidgets.QTreeWidgetItem, key: Any, label: str,
                                storage_dict: Dict[Any, QtWidgets.QTreeWidgetItem]) -> QtWidgets.QTreeWidgetItem:
        """
        Create a new QTreeWidgetItem under 'parent' with a specified 'label' if the 'key' is not present in
        'storage_dict'. If the 'key' is already present, retrieve the existing QTreeWidgetItem from 'storage_dict'.
        The function expands the tree item and returns it.

        :param parent: (QtWidgets.QTreeWidgetItem) The parent item under which the new item will be
                        created or retrieved.
        :param key: (Any) The key used to check for existing items in 'storage_dict' and to store the new item.
        :param label: (str) The label for the new tree item.
        :param storage_dict: (Dict[Any, QtWidgets.QTreeWidgetItem]) A dictionary storing tree items with their
                        corresponding keys.

        :return QtWidgets.QTreeWidgetItem: The created or retrieved tree item.
        """
        if key not in storage_dict:
            item = QtWidgets.QTreeWidgetItem(parent, [label])
            storage_dict[key] = item
            self.pluginTreeWidget.expandItem(item)
        return storage_dict[key]

    def create_item_widget(self, tree_item: QtWidgets.QTreeWidgetItem, plugin_id: str, mandatory: bool,
                           column_index: int, widget_type: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """
        Create and configure a widget for a given tree item in a plugin tree.

        This function creates a widget of the specified type and configures it based on whether
        it is mandatory. It places the widget in a specified column of the tree item and connects
        its state change signals to a handler function.

        :param tree_item: (QtWidgets.QTreeWidgetItem) The tree item to which the widget will be added.
        :param plugin_id: (str) Identifier for the plugin associated with this widget.
        :param mandatory: (bool) Flag indicating whether the widget is mandatory (not user-editable).
        :param column_index: (int) The column index in the tree item where the widget will be placed.
        :param widget_type: (QtWidgets.QWidget) The type of widget to create (e.g., QCheckBox, QComboBox).

        :return QtWidgets.QWidget: The created and configured widget.
        """
        # Create an item widget for the plugin
        item_widget = widget_type
        item_widget.is_overriden = False
        item_widget.setEnabled(not mandatory)  # Lock the item widget

        # Place the item widget in the specified column of the tree item of the tree widget.
        self.pluginTreeWidget.setItemWidget(tree_item, column_index, item_widget)

        connection = (
            lambda state,
            unique_id=plugin_id,
            item=tree_item: self.on_widget_state_changed(state, unique_id, item, column_index)
        )

        # Connect the item_widget state change signal
        if isinstance(item_widget, QtWidgets.QCheckBox):
            item_widget.stateChanged.connect(connection)
        if isinstance(item_widget, QtWidgets.QComboBox):
            item_widget.currentTextChanged.connect(connection)

        return item_widget

    def populate_plugin(self, plugin_id: str, plugin_data: Dict[str, Any]) -> None:
        """
        Populates the plugin tree with the provided plugin data. This function creates tree items
        for the plugin's package, type, and category, and adds a plugin item under the appropriate
        category. It also creates a checkbox and, if applicable, a failure response combobox for
        the plugin.

        :param plugin_id: (str) The unique identifier for the plugin.
        :param plugin_data: (Dict[str, Any]) A dictionary containing the plugin's data, such as
        module path, category, label, and class.

        """
        module_path = plugin_data["module_path"]
        module_path_parts = module_path.split('.')
        plugin_package = module_path_parts[-4]
        plugin_type = module_path_parts[-2]
        plugin_category = plugin_data["plugin_category"]
        mandatory = plugin_data.get("mandatory", False)  # Get the mandatory flag, default to False if not present

        # Create or get the plugin package item
        plugin_package_key = plugin_package
        plugin_package_item = self.create_or_get_tree_item(self.pluginTreeWidget, plugin_package_key, plugin_package,
                                                           self.plugins_packages)

        # Create or get the plugin type item
        plugin_type_key = (plugin_package, plugin_type)
        plugin_type_item = self.create_or_get_tree_item(plugin_package_item, plugin_type_key, plugin_type,
                                                        self.plugins_types)
        parent_item = plugin_type_item

        # Create or get the plugin category item, only if plugin_category is not None and not "None"
        if plugin_category and plugin_category != "None":
            plugin_category_key = (plugin_type_key, plugin_category)
            plugin_category_item = self.create_or_get_tree_item(plugin_type_item, plugin_category_key, plugin_category,
                                                                self.plugins_categories)
            parent_item = plugin_category_item

        # Create the final item (plugin)
        final_item_name = plugin_data["plugin_label"]
        final_item = QtWidgets.QTreeWidgetItem(parent_item, [final_item_name])
        self.pluginsData[plugin_id]["treeWidgetItem"] = final_item

        # Store plugin_id as a data attribute in the tree item
        final_item.setData(0, QtCore.Qt.UserRole, plugin_id)

        # Create an activation checkbox for the plugin
        checkbox = self.create_item_widget(final_item, plugin_id, mandatory, 1, QtWidgets.QCheckBox())
        checkbox.setChecked(mandatory)  # Set checked

        # Create a failure response combobox if the plugin is not a collector
        if not plugin_data['plugin_class'].order < pyblish.api.ValidatorOrder:
            failure_combobox = self.create_item_widget(final_item, plugin_id, mandatory, 2, WheelIgnoredComboBox())
            failure_combobox.addItems(["fail", "warning"])

        if mandatory:
            final_item.setToolTip(0, "This plugin is mandatory and cannot be disabled")

    def populate_plugins(self) -> None:
        """ Populates the plugin tree widget with plugins data.

        This function iterates through all plugins stored in 'self.pluginsData', creates or retrieves
        the necessary tree items for each plugin, and adds them to the plugin tree widget.
        It also connects the tree widget's item selection changed signal to a handler function.

        This function assumes that 'self.pluginTreeWidget' is an instance of a tree widget
        (like QtWidgets.QTreeWidget), and 'self.pluginsData' is a dictionary containing
        plugin data.
        """
        self.pluginTreeWidget.clear()

        for plugin_id, plugin_data in self.pluginsData.items():
            self.populate_plugin(plugin_id, plugin_data)

        # Connect the item selection changed signal
        self.pluginTreeWidget.itemSelectionChanged.connect(self.on_plugin_item_selected)

    def create_connections(self):
        """ Establishes connections between UI elements and their corresponding actions.

        This method sets up signal-slot connections for various interactive components of the UI,
        like combo boxes, buttons, and checkboxes. These connections ensure that when a user
        interacts with a component, the appropriate method or action is triggered.
        """

        def toggle_advanced_options(checked: bool):
            """ Toggles the visibility of the advanced options group box.

            :param checked: (bool) The state of the advanced options' checkbox.
            """
            # Show or hide the advanced group box based on the checkbox state
            self.advancedGroupBox.setVisible(checked)

        def on_task_changed(new_task: str):
            """ Handles the change in selected task from the task combo box.

            :param new_task: (str) The newly selected task.
            """
            if new_task != self.currentTask:
                self.currentTask = new_task
                selected_asset_type = self.assetTypeComboBox.currentText()
                self.update_ui_with_task_settings(selected_asset_type, new_task)

        def on_asset_type_changed(asset_type: str):
            """ Handles the change in selected asset type from the asset type combo box.

            :param asset_type: (str) The newly selected asset type.
            """
            self.taskComboBox.clear()
            tasks = self.assetTasksMapping.get(asset_type, [])
            self.taskComboBox.addItems(tasks)
            if tasks:
                self.update_ui_with_task_settings(asset_type, tasks[0])

        self.taskComboBox.currentTextChanged.connect(on_task_changed)
        self.assetTypeComboBox.currentTextChanged.connect(on_asset_type_changed)
        self.saveButton.clicked.connect(self.on_save)
        self.resetButton.clicked.connect(self.on_reset)

        # Connect the advanced options checkbox
        self.advancedOptionsCheckbox.toggled.connect(toggle_advanced_options)

        # Connect the dump JSON button
        self.dumpPluginsDataJsonButton.clicked.connect(self.on_dump_json)

    def update_ui_with_task_settings(self, asset_type: str, task: str):
        """ Updates the UI with specific settings for a given task and asset type.

        This method goes through each plugin and updates its UI elements, such as checkboxes
        and combo boxes, based on the settings associated with the specified asset type and task.

        :param asset_type: (str) The selected asset type.
        :param task: (str) The selected task.
        """
        # Retrieve the settings for the specified asset type and task
        task_settings = self.plugins_settings.get(asset_type, {}).get(task, {})

        # Iterate through all the plugins and update their UI elements
        for plugin_id, plugin_data in self.pluginsData.items():
            tree_item = plugin_data.get("treeWidgetItem")

            if tree_item:

                # Update the checkbox state
                checkbox = self.pluginTreeWidget.itemWidget(tree_item, 1)
                if checkbox and checkbox.isEnabled():
                    # Extract only the 'active' boolean value from the settings
                    module_active_state = task_settings.get(plugin_id, {}).get("active", False)
                    checkbox.setChecked(module_active_state)
                    self.set_row_color(tree_item, self.DEFAULT_COLOR)
                else:
                    self.set_row_color(tree_item, self.LOCKED_COLOR)

                # Update the failure response combo box
                failure_response_combobox = self.pluginTreeWidget.itemWidget(tree_item, 2)
                if failure_response_combobox:
                    failure_response_combobox.setCurrentText(
                        task_settings.get(plugin_id, {}).get('failure_response', 'fail'))

    def set_row_color(self, tree_item: QtWidgets.QTreeWidgetItem, color: str):
        """ Sets the color of a row in the plugin tree widget.

        This method changes the foreground color of the text in each column
        of the specified tree item and adjusts the color of any widget present in the row.
        It supports changing the color of checkboxes and combo boxes.

        :param tree_item: (QTreeWidgetItem) The tree item whose row color is to be set.
        :param color: (str) The color to apply, as a string name or hexadecimal value.
        """
        # Iterate through each column in the row
        for column in range(self.pluginTreeWidget.columnCount()):

            # Change the text color of the item in the column
            tree_item.setForeground(column, QtGui.QBrush(QtGui.QColor(color)))

            # Retrieve the widget in this column
            item_widget = self.pluginTreeWidget.itemWidget(tree_item, column)

            # If the widget is a checkbox, apply the color to the checkbox
            if isinstance(item_widget, QtWidgets.QCheckBox):
                self.set_checkbox_color(item_widget, color)

            # If the widget is a combo box, apply the color to the combo box
            if isinstance(item_widget, QtWidgets.QComboBox):
                self.set_combobox_color(item_widget, color)

    def set_plugin_label_color(self, tree_item: QtWidgets.QTreeWidgetItem):
        """ Sets the color of a plugin label based on whether it has been overridden.

        This method checks if any widget in the row (checkbox or combobox) has been marked
        as overridden. If any widget is overridden, it sets the color of the first column
        in the tree item to the overridden color. Otherwise, it sets it to the default color.

        :param tree_item: (QTreeWidgetItem) The tree item representing a plugin row in the tree widget.
        """
        # Flag to track if any widget in the row is overridden
        item_is_overriden = False

        # Iterate through each column in the row to check for overridden widgets
        for column in range(self.pluginTreeWidget.columnCount()):
            # Retrieve the widget in this column
            item_widget = self.pluginTreeWidget.itemWidget(tree_item, column)
            # Check if the widget exists and is marked as overridden
            if item_widget and item_widget.is_overriden:
                item_is_overriden = True
                break  # No need to check other columns if one is overridden

        # Set the foreground color for the first column (plugin label) based on the override status
        if item_is_overriden:
            tree_item.setForeground(0, QtGui.QBrush(QtGui.QColor(self.OVERRIDEN_COLOR)))
        else:
            tree_item.setForeground(0, QtGui.QBrush(QtGui.QColor(self.DEFAULT_COLOR)))

    @staticmethod
    def set_checkbox_color(checkbox: QtWidgets.QCheckBox, color: str):
        """ Sets the color of a checkbox and its indicator in a tree item.

        This method applies a custom stylesheet to the given checkbox to change
        its text color and the color of its unchecked indicator.

        :param checkbox: (QCheckBox) The checkbox whose color is to be set.
        :param color: (str) The color to apply to the checkbox and its indicator.
        """

        # Define the stylesheet for the checkbox
        style = f"""
            QCheckBox {{
                color: {color};
            }}
            QCheckBox::indicator:unchecked {{
                border-color: {color};
            }}
        """

        # Apply the stylesheet to the checkbox
        checkbox.setStyleSheet(style)

    @staticmethod
    def set_combobox_color(combobox: QtWidgets.QComboBox, color: str):
        """ Sets the text color of a combobox in a tree item.

        This method applies a custom stylesheet to the given combobox to change
        its text color.

        :param combobox: (QComboBox) The combobox whose text color is to be set.
        :param color: (str) The color to apply to the combobox text.
        """

        # Define the stylesheet for the combobox
        style = f"""
            QComboBox {{
                color: {color};
            }}
        """

        # Apply the stylesheet to the combobox
        combobox.setStyleSheet(style)

    def on_widget_state_changed(self, state: Union[int, str], plugin_id: str, tree_item: QtWidgets.QTreeWidgetItem,
                                column: int):
        """ Handles changes in the state of widgets (checkboxes and combo boxes) representing plugin settings.

        This method compares the new state of a widget against its saved state in the settings.
        If there's a discrepancy, the widget's color is set to 'overridden', otherwise, it reverts to the default color.

        :param state: (Union[int, str]) The new state of the widget.
                                        For checkboxes, it's Qt.CheckState; for combo boxes, it's the current text.
        :param plugin_id: (str) The identifier of the plugin module.
        :param tree_item: (QTreeWidgetItem) The tree item in the plugin tree widget.
        :param column: (int) The column index of the widget in the tree item.
        """
        # Retrieve the currently selected asset type and task from the combo boxes
        selected_asset_type = self.assetTypeComboBox.currentText()
        selected_task = self.taskComboBox.currentText()

        # Access the saved settings for the selected asset type and task, specifically for this plugin
        saved_state = self.plugins_settings.get(selected_asset_type, {}).get(selected_task, {}).get(
            plugin_id, {})

        # Fetch the widget (either a checkbox or combobox) from the given column in the tree item
        item_widget = self.pluginTreeWidget.itemWidget(tree_item, column)

        # Handle state changes for checkboxes
        if isinstance(item_widget, QtWidgets.QCheckBox):
            saved_state = saved_state.get("active", False)
            if (state == QtCore.Qt.Checked) != saved_state:
                # State differs from saved state, set color to orange
                item_widget.is_overriden = True
                self.set_checkbox_color(item_widget, self.OVERRIDEN_COLOR)
            else:
                # State matches the saved state, set color to default
                item_widget.is_overriden = False
                self.set_checkbox_color(item_widget, self.DEFAULT_COLOR)

        # Handle state changes for combo boxes
        if isinstance(item_widget, QtWidgets.QComboBox):
            saved_state = saved_state.get("failure_response", 'fail')
            if state != saved_state:
                # State differs from saved state, change color to orange
                item_widget.is_overriden = True
                self.set_combobox_color(item_widget, self.OVERRIDEN_COLOR)
            else:
                # State matches the saved state, revert color to default
                item_widget.is_overriden = False
                self.set_combobox_color(item_widget, self.DEFAULT_COLOR)

        # Update the color of the plugin label based on the overridden state
        self.set_plugin_label_color(tree_item)

        # Update the active state in the pluginsData
        self.pluginsData[plugin_id]["active"] = bool(state)

    def on_plugin_item_selected(self):
        """ Handles the selection event on the plugin items in the tree widget.

        When a plugin item is selected, this method displays the plugin's
        detailed information in a separate tab. If no plugin is selected or
        a non-plugin item is selected, it clears or closes the details tab.

        This method assumes that each plugin item in the tree widget stores
        its unique identifier (plugin_id) as user data.
        """
        # Retrieve all selected items from the plugin tree widget
        selected_items = self.pluginTreeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            # Fetch the plugin_id stored in the tree item's user data
            plugin_id = selected_item.data(0, QtCore.Qt.UserRole)

            if plugin_id:
                # Fetch the plugin data using its unique identifier
                plugin = self.pluginsData.get(plugin_id)
                if plugin:
                    # Add a tab in the UI to display the details of the selected plugin
                    self.add_plugin_details_tab(plugin)
            else:
                # Clear or close the details tab if the selected item is not a plugin
                self.clear_or_close_details_tab()

    def add_plugin_details_tab(self, plugin_data: dict):
        """ Adds a new tab with details for the selected plugin.

        :param plugin_data: (dict) Data of the selected plugin. This data is used to populate
                                the details tab with relevant information about the plugin.

        This method creates a new instance of `PluginDetailsTab`, passing the plugin data,
        and adds this tab to the `tabWidget`. If a details tab already exists, it replaces
        the current details tab. The tab is also made closable and a method to handle tab
        closing is connected.
        """
        def close_tab(index: int):
            """ Closes a tab in the tab widget.

            :param index: (int) The index of the tab to be closed.
            """
            # Remove the tab at the specified index
            self.tabWidget.removeTab(index)
            # If the closed tab is the details tab, reset the detailsTabIndex
            if index == self.DETAILS_TAB_INDEX:
                self.DETAILS_TAB_INDEX = -1

        # Create a new PluginDetailsTab instance with plugin data
        detail_tab = PluginDetailsTab(plugin_data, self)

        # Define the title for the tab
        tab_title = f"Plugin: {plugin_data['plugin_label']}"

        # If a details tab already exists, replace it
        if self.DETAILS_TAB_INDEX != -1:
            self.tabWidget.removeTab(self.DETAILS_TAB_INDEX)

        # Add the new details tab to the tab widget and update the index
        self.DETAILS_TAB_INDEX = self.tabWidget.addTab(detail_tab, tab_title)

        # Set the newly added tab as the current tab
        self.tabWidget.setCurrentIndex(self.DETAILS_TAB_INDEX)

        # Make the tabs in the tab widget closable
        self.tabWidget.setTabsClosable(True)

        # Connect the tab close request signal to the close_tab function
        self.tabWidget.tabCloseRequested.connect(close_tab)

    def clear_or_close_details_tab(self):
        """ Clears or closes the details tab in the UI.

        This method removes the details tab from the tab widget if it exists.
        It is typically called when a non-plugin item is selected or no item
        is selected in the plugin tree widget.

        The details tab index is tracked by `self.detailsTabIndex`, which is
        set to -1 when there is no details tab open.
        """

        # Check if the details tab index is valid (not -1)
        if self.DETAILS_TAB_INDEX != -1:
            # If a details tab exists, remove it from the tab widget
            self.tabWidget.removeTab(self.DETAILS_TAB_INDEX)
            # Reset the details tab index to indicate that no details tab is open
            self.DETAILS_TAB_INDEX = -1

    def on_save(self):
        """ Saves the current plugin settings for the selected asset type and task.

        This method updates the settings for each plugin based on the current state of
        the UI elements (checkboxes and combo boxes) and writes these updated settings
        back to the file specified for plugin settings. After saving, the UI is reset
        to reflect the newly saved state.
        """
        # Retrieve the currently selected asset type and task from the combo boxes
        selected_asset_type = self.assetTypeComboBox.currentText()
        selected_task = self.taskComboBox.currentText()

        # Read the current settings from the file
        current_settings = self.read_json_file(self.plugins_settings_file)

        # Retrieve the settings for the selected asset type and task, or initialize if not present
        asset_type_settings = current_settings.get(selected_asset_type, {})
        task_specific_settings = asset_type_settings.get(selected_task, {})

        # Update settings for each plugin based on the state of its corresponding UI elements
        for plugin_id, plugin_data in self.pluginsData.items():

            # Get the tree item corresponding to the plugin
            tree_item = plugin_data.get("treeWidgetItem")
            if tree_item:
                # Retrieve the checkbox and combobox for the plugin
                checkbox = self.pluginTreeWidget.itemWidget(tree_item, 1)
                failure_response_combobox = self.pluginTreeWidget.itemWidget(tree_item, 2)

                # Determine the failure response from the combobox, if it exists
                if failure_response_combobox:
                    failure_response = failure_response_combobox.currentText()
                else:
                    failure_response = None

                # Update the settings for the plugin
                if checkbox:
                    task_specific_settings[plugin_id] = {
                        "name": plugin_data["plugin_label"].split('.'),
                        "active": checkbox.isChecked(),
                        "failure_response": failure_response
                    }

        # Update the task-specific settings in the asset type settings
        asset_type_settings[selected_task] = task_specific_settings

        # Update the asset type settings in the current settings
        current_settings[selected_asset_type] = asset_type_settings

        # Write the updated settings back to the file
        self.write_plugins_settings(current_settings)

        # Reset the UI to reflect the new state after saving
        self.on_reset()

    def on_reset(self):
        """ Resets the UI to reflect the saved plugin settings
        for the currently selected asset type and task.

        This method reads the saved plugin settings from the file and updates
        the UI elements (checkboxes and combo boxes) to reflect these settings.
        """
        # Read the saved plugin settings from the file
        self.plugins_settings = self.read_json_file(self.plugins_settings_file)

        # Retrieve the currently selected asset type and task from the combo boxes
        selected_asset_type = self.assetTypeComboBox.currentText()
        selected_task = self.taskComboBox.currentText()

        # Update the UI with the settings for the selected asset type and task
        self.update_ui_with_task_settings(selected_asset_type, selected_task)

    def on_dump_json(self):
        """ Dumps the plugins data to a JSON file located at a predefined path.

        This method collects the current plugins' data, including their states and settings,
        and writes this data to a JSON file. This can be used for debugging or analysis purposes.
        A message box is shown to the user upon successful saving of the JSON file.
        """

        # Define the path where the JSON file will be saved
        output_json_path = "/tmp/plugins_data.json"

        # Collect the current plugins data without reloading from the environment
        collected_plugins_data = self.generator.collect_plugins_data(False)

        # Dump the collected plugins data to the specified JSON file
        self.generator.dump_json_file(output_json_path, {'plugins_data': collected_plugins_data})

        # Show a message box to inform the user that the JSON file has been successfully saved
        QtWidgets.QMessageBox.information(self, "JSON Dump", f"JSON file saved to {output_json_path}")

    @staticmethod
    def read_json_file(json_file: str) -> dict:
        """ Reads a JSON file and returns its contents as a dictionary.

        :param json_file: (str) The path to the JSON file to read.

        Returns:
            dict: The contents of the JSON file as a dictionary.

        Raises:
            FileNotFoundError: If the specified JSON file does not exist.
        """
        try:
            with open(json_file, 'r') as file:
                return json.load(file)

        except FileNotFoundError:
            # Return an empty dictionary if the file does not exist
            print(f"Error: The file '{json_file}' does not exist.")
            return {}

    def write_plugins_settings(self, task_settings: dict) -> None:
        """ Writes the provided plugin settings to a JSON file.

        This method saves the given plugin settings to a JSON file specified by the
        'self.plugins_settings_env_var' attribute. The settings are expected to be in
        the form of a dictionary.

        :param task_settings: (dict) A dictionary containing the plugin settings to be saved.
        """

        # Open the file specified in 'plugins_settings_env_var' in write mode
        with open(self.plugins_settings_file, 'w') as file:
            # Write the task settings to the file in a readable format (pretty-printed JSON)
            json.dump(task_settings, file, indent=4)

        # Log a message indicating successful save operation
        log.info(f"{self.plugins_settings_file} saved.")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """ Handles the event triggered when the dialog window is closed.

        This method is automatically called when the dialog window is about to be closed.
        It logs an informational message indicating that the Plugins Manager window is closing,
        and then performs the standard close event procedure as defined in the super class.

        :param event: (QtGui.QCloseEvent) The close event object.
        """

        # Log an informational message about the closing of the Plugins Manager window
        log.info("Closing Plugins Manager window.")

        # Call the closeEvent of the parent class to ensure standard closing procedures are performed
        super(PluginsManagerUI, self).closeEvent(event)


class PluginDetailsTab(QtWidgets.QWidget):
    """ A widget representing a tab in the UI that displays detailed information about a plugin.

    This tab includes the documentation and file path information of the given plugin, providing
    a concise and detailed view of important plugin attributes.

    Attributes:
        layout (QtWidgets.QVBoxLayout): The vertical box layout used for organizing child widgets.
    """

    def __init__(self, plugin_data: dict, parent: QtWidgets.QWidget = None) -> None:
        """ Initializes the PluginDetailsTab instance with plugin data and an optional parent widget.

        This method sets up the layout for the tab and populates it with a label that
        displays the documentation and file path of the plugin.

        :param plugin_data: (dict) Data about the plugin, including documentation and file path.
        :param parent: (QtWidgets.QWidget, optional) Parent widget. Defaults to None.
        """
        super(PluginDetailsTab, self).__init__(parent)

        # Initialize the layout for this widget
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(10)

        # Add a placeholder label to the layout
        self.layout.addWidget(QtWidgets.QLabel("Plugin Details:\n\n\n\n"))

        # Retrieve plugin documentation, default to a placeholder if not available
        plugin_doc = plugin_data.get('plugin_doc', 'No documentation available.')

        # Retrieve plugin file path
        plugin_filepath = plugin_data["plugin_filepath"]

        # Construct the text for the label including plugin documentation and file path
        tab_text = f'{plugin_doc} \n\n\n File path: \n {plugin_filepath}'

        # Create a label with the constructed text
        label = QtWidgets.QLabel(tab_text)

        # Enable word wrapping for the label to ensure text fits within the widget
        label.setWordWrap(True)

        # Add the label with plugin details to the layout
        self.layout.addWidget(label)


class CustomTreeWidget(QtWidgets.QTreeWidget):
    """ A custom tree widget that extends the functionality of QTreeWidget.

    This widget is designed to handle specific interactions, such as displaying
    a context menu with options to manipulate the state of its items.
    """
    def __init__(self, parent=None):
        """ Initializes the CustomTreeWidget instance with an optional parent widget.

        :param parent: (QtWidgets.QWidget, optional) Parent widget. Defaults to None.
        """
        super(CustomTreeWidget, self).__init__(parent)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        """ Handles the context menu event, typically triggered by a right-click on the widget.

        This method creates a context menu at the cursor's position with options to
        manipulate the state of child items of a tree item.

        :param event: (QtGui.QContextMenuEvent) The event object containing context menu event information.

        In Qt, the contextMenuEvent method is triggered whenever a context menu event occurs.
        By default, this event is commonly associated with a right-click (secondary mouse button click) on the widget.
        """
        item = self.itemAt(event.pos())
        """
        The itemAt method is a function of the tree widget (self refers to the instance of CustomTreeWidget).
        This method takes a QPoint as an argument and returns the tree widget item (QTreeWidgetItem) that is located
        at the given position. If there is no item at that position (for instance, if the user right-clicked on an 
        empty area of the tree widget), itemAt will return None.
        """
        if item and item.childCount() > 0:  # Check if item has children
            menu = QtWidgets.QMenu(self)
            """
            QtWidgets.QMenu: QMenu is a class in the Qt framework (specifically in the QtWidgets module) that provides 
            a means to create menus. A menu is a list of actions or options that a user can choose from. 
            Menus are commonly seen as context menus (that appear on right-click), as well as in menu bars 
            at the top of applications.

            Creating a New Menu Instance: QtWidgets.QMenu(self) creates a new instance of QMenu. 
            The self argument is passed to the QMenu constructor.
            In this context, self refers to the instance of CustomTreeWidget class (which, in turn, is a subclass 
            of QTreeWidget). By passing self, you are setting the CustomTreeWidget as the parent of the QMenu. 
            This ensures that the menu is displayed in the correct context and aligns with the overall widget 
            hierarchy of your application.

            Assigning to menu: The newly created QMenu object is assigned to the variable menu.
            This variable is used to refer to and manipulate the menu in subsequent lines of code.

            In summary, menu = QtWidgets.QMenu(self) is initializing a new context menu within the CustomTreeWidget 
            and assigning it to the variable menu for further use, such as adding actions to it or displaying it.
            The menu will appear in the context of the CustomTreeWidget instance when triggered, 
            typically by a right-click event.
            """
            check_all_action = menu.addAction("activate all")
            uncheck_all_action = menu.addAction("deactivate all")
            menu.addSeparator()
            all_fail_action = menu.addAction("set all to 'fail'")
            all_warning_action = menu.addAction("set all to 'warning'")

            action = menu.exec_(self.mapToGlobal(event.pos()))
            """
            event.pos(): This function call returns the position of the mouse click event relative to the widget that 
            received the event. In the context of your contextMenuEvent function, event.pos() gives the coordinates 
            of the right-click inside your CustomTreeWidget.

            self.mapToGlobal(event.pos()): The mapToGlobal function translates the local widget coordinates 
            (from event.pos()) to global screen coordinates. This is necessary because the position where the 
            context menu pops up needs to be specified in global screen coordinates.

            menu.exec_(): This function displays the context menu at the specified position and then blocks 
            the program's execution while the menu is open. The menu waits for the user to select an action or 
            click away from the menu.

            action = menu.exec_(...): The exec_ function returns the action that was selected by the user. 
            This returned value is stored in the variable action. If the user selects an action from the menu 
            (like "activate all" or "deactivate all"), that action object is returned. If the user clicks away from 
            the menu without making a selection, exec_ returns None.
            """

            if action == check_all_action:
                self.set_child_items_value(item, 1, True)
            elif action == uncheck_all_action:
                self.set_child_items_value(item, 1, False)
            elif action == all_fail_action:
                self.set_child_items_value(item, 2, 'fail')
            elif action == all_warning_action:
                self.set_child_items_value(item, 2, 'warning')

    def set_child_items_value(self, parent_item: QtWidgets.QTreeWidgetItem,
                              column: int, value: Union[bool, str]) -> None:
        """ Recursively updates the checkbox state of all child items of the given parent item.

        This function iterates through each child of the parent item. If the child is a leaf node
        (i.e., it has no further child items), the value of this child is updated.
        If the child is not a leaf node (i.e., it has its own child items), the function
        recursively updates the values of these child items.

        :param parent_item: The parent item whose child items' values are to be updated.
        :param column: (int) The column ...
        :param value: The value to set the children to.
        """
        # Iterate through all child items of the given parent item
        for index in range(parent_item.childCount()):
            # Retrieve the child item at the current index
            child_item = parent_item.child(index)

            # Check if the child item has no further child items of its own (leaf node)
            if child_item.childCount() == 0:
                # If it's a leaf node, change the value
                if column == 1:
                    self.set_checkbox_state(child_item, value)
                elif column == 2:
                    self.set_failure_response(child_item, value)
            else:
                # If the child item has its own children (non-leaf node),
                # make a recursive call to process its children
                self.set_child_items_value(child_item, column, value)

    def set_checkbox_state(self, item: QtWidgets.QTreeWidgetItem, state: bool) -> None:
        """ Sets the state of the checkbox for a given tree item if the checkbox is enabled.

        This function checks if the checkbox of the given item is enabled. If the checkbox is enabled,
        its state is updated according to the 'state' parameter. If the checkbox is disabled (locked),
        the state is not altered.

        :param item: The tree item whose checkbox state is to be set.
        :param state: The state to set the checkbox to. True for checked, False for unchecked.
        """
        # Retrieve the checkbox widget associated with the tree item
        checkbox = self.itemWidget(item, 1)

        # Check if the checkbox is present and enabled
        if checkbox and checkbox.isEnabled():
            # If the checkbox is enabled, update its state
            checkbox.setChecked(state)

    def set_failure_response(self, item: QtWidgets.QTreeWidgetItem, failure_response: str) -> None:
        """ Sets the state of the checkbox for a given tree item if the checkbox is enabled.

        This function checks if the checkbox of the given item is enabled. If the checkbox is enabled,
        its state is updated according to the 'state' parameter. If the checkbox is disabled (locked),
        the state is not altered.

        :param item: The tree item whose checkbox state is to be set.
        :param failure_response: The failure response to set the item to ('fail' or 'warning').
        """
        # Retrieve the checkbox widget associated with the tree item
        failure_response_combobox = self.itemWidget(item, 2)

        # Check if the checkbox is present and enabled
        if failure_response_combobox:
            # If the checkbox is enabled, update its state
            failure_response_combobox.setCurrentText(failure_response)


class WheelIgnoredComboBox(QtWidgets.QComboBox):
    """ A custom combo box widget that ignores mouse wheel events.

    This widget is an extension of the standard QComboBox. It is specifically designed to prevent
    accidental changes to its value when the user scrolls with the mouse wheel.
    """
    def __init__(self, parent=None):
        """ Initializes the WheelIgnoredComboBox instance with an optional parent widget.

        :param parent: (QtWidgets.QWidget, optional) Parent widget. Defaults to None.
        """
        super(WheelIgnoredComboBox, self).__init__(parent)

    @staticmethod
    def wheelEvent(event: QtGui.QWheelEvent) -> None:
        """ Overrides the wheel event handler to ignore mouse wheel events.

        This method is invoked automatically whenever a wheel event occurs on the combo box.
        By calling 'ignore' on the event, it prevents the default behavior of changing the combo box value
        when the mouse wheel is used.

        :param event: (QtGui.QWheelEvent) The event object containing information about the wheel event.
        """
        event.ignore()  # Prevents the combo box from reacting to the wheel event


def open_plugins_manager() -> None:
    """
    Opens or brings to the foreground the Plugins Manager UI within the main application.

    This function checks if an instance of the Plugins Manager UI already exists in the
    main application. If it does, the existing instance is brought to the foreground.
    Otherwise, a new instance is created and shown. This approach ensures that only one
    instance of the Plugins Manager UI is open at a time.

    Assumes that the main application is a `QtWidgets.QApplication` instance and uses
    its attribute `plugins_manager_ui` to store the UI instance.
    """
    # Retrieve the instance of the main application
    main_app = QtWidgets.QApplication.instance()

    # Check if the plugins manager UI already exists
    if not hasattr(main_app, 'plugins_manager_ui'):
        # Create and show a new instance if it doesn't exist
        main_app.plugins_manager_ui = PluginsManagerUI()
        main_app.plugins_manager_ui.show()
    else:
        # Bring the existing instance to the foreground
        main_app.plugins_manager_ui.raise_()
        main_app.plugins_manager_ui.activateWindow()
