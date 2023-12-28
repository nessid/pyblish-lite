import pyblish.api
import maya.cmds as cmds
import re
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_utilities.result_by_plugin_type import validation_result
from pyblish_core.plugins_utilities.strings_handling import define_basename
from pyblish_core.plugins_utilities.strings_handling import remove_pattern
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class NameShadingNodesValidator(pyblish.api.Validator):
    """Name | Shading Nodes Validator

    This Pyblish validator plugin enforces specific naming conventions for shading nodes:
    - Surface Shaders: 'SHD_{basename}'.
    - Shading Groups: Named as '{basename}SG'.

    Important guidelines to follow:
    - Basenames must use camelCase without underscores and should not include any shader type references.

    Notes:
    - The naming of shading engines is determined by the surface shader, not the other way around.
    - Only surface shaders are validated, as the shading engine is automatically renamed by removing the surface shader prefix and adding the shading engine suffix. Once the surface shader name is valid, the shading engine's name will be valid as well.

    This plugin ensures that shading nodes in your scene adhere to the specified naming conventions.
    """
    plugin_id = '5bb6481e-a25a-4a51-81b7-f18a239226f5'  # https://www.uuidgenerator.net/version4
    category = 'Name'
    name = 'Shading nodes'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    families = ['model_nodes']
    actions = []

    order = pyblish.api.ValidatorOrder + 0.022

    def process(self, context, instance):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        :param instance: (pyblish.actions.Instance): Instance that meets the plugin requirements.
        """
        # Retrieve shading groups nodes from the context data
        shading_engines = context.data['shading_groups']

        # Retrieve excluded nodes from the context data
        excluded_nodes = context.data['excluded_nodes']

        # Retrieve all available shader types in Maya
        shader_types = cmds.listNodeTypes('shader')

        # Retrieve shading nodes affixes mapping from the context data
        shading_affix_mapping = context.data['shading_affix_mapping']

        # Retrieve the list of nodes from the instance data
        model_nodes = instance.data['nodes']

        # Exclude excluded nodes
        shading_engines = list(set(shading_engines) - set(excluded_nodes))

        failed_nodes = []
        renamable_nodes = {}
        invalid_basename = []

        for shading_engine in shading_engines:
            # Query assigned objects for the current shading engine
            assigned_objects = cmds.sets(shading_engine, query=True)
            if not assigned_objects:
                continue

            # List assigned objects long name
            assigned_objects = cmds.ls(assigned_objects, long=True)

            # Exclude excluded nodes from assigned_objects
            assigned_objects = list(set(assigned_objects).intersection(model_nodes))
            assigned_objects = list(set(assigned_objects) - set(excluded_nodes))
            if not assigned_objects:
                continue

            # Get the surface shader connected to the shading engine
            surface_shader = cmds.listConnections(shading_engine + '.surfaceShader',
                                                  connections=True, source=True, destination=False)

            if not surface_shader:
                continue

            surface_shader = surface_shader[1]

            shader_name = surface_shader

            # Extract the shortname and basename
            node_short_name, basename = define_basename(self, context, shader_name)

            cmds.rename(shading_engine,
                        f"{remove_pattern(node_short_name, shading_affix_mapping['surfaceShader'])}"
                        f"{shading_affix_mapping['shadingEngine']}"
                        )

            has_underscore = len(basename.split('_')) > 1
            is_upper = basename.isupper()
            is_shader_type = re.sub(r'\d', '', basename).lower() in [item.lower() for item in shader_types]

            if has_underscore or is_upper or is_shader_type or basename.isdigit() or not basename:
                invalid_basename.append(surface_shader)
                self.log.warning(f"{surface_shader} has an invalid basename: '{basename}'. Please use a camelCase"
                                 f" basename with no underscores and no shader type.")
                continue

            required_surface_shader_name = f"{shading_affix_mapping['surfaceShader']}_{basename}"

            # Check if the surface shader has the required name
            if not surface_shader == required_surface_shader_name:
                # If the surface shader has an incorrect name, add it to the failed_nodes list
                failed_nodes.append(surface_shader)
                self.log.warning(f"Surface shader '{surface_shader}' has an incorrect name. "
                                 f"Required: '{required_surface_shader_name}'")
                renamable_nodes[surface_shader] = required_surface_shader_name

        # Actions
        if failed_nodes:
            # Create 'Select' actions subclass
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'surface shader(s) with incorrect name',
                                                                 failed_nodes + invalid_basename
                                                                 )
            self.actions.append(select_failed_nodes)

        if renamable_nodes:
            # Create 'Rename' actions subclass
            rename_failed_nodes = actions.create_action_subclass(actions.Rename,
                                                                 'surface shader(s) with valid basename',
                                                                 renamable_nodes
                                                                 )
            self.actions.append(rename_failed_nodes)

        if invalid_basename:
            # Create 'Select' actions subclass
            select_failed_nodes = actions.create_action_subclass(actions.Select,
                                                                 'surface shader(s) with invalid basename',
                                                                 invalid_basename
                                                                 )
            self.actions.append(select_failed_nodes)

        validation_result(self, 'shading node(s) with incorrect name',
                          failed_nodes + invalid_basename,
                          self.failure_response)
