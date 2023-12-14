import pyblish.api
import maya.cmds as cmds
from pyblish_plugins.pyblish_plugins_maya import actions
from pyblish_core.plugins_results import validation_result
from pyblish_core.results_lib import generate_result_message
from pyblish_core.name_lib import define_plugin_label


class FixShading(pyblish.api.Action):
    """Fix | Shading

    This Pyblish action replaces creates and connects a surface shader of the 'required_shader_type' (collected in the validation data collector) to shading engines that have failed validation.

    If a surface shader was connected, it transfers the common attributes and color map connection from the previously assigned shader to the new one, deletes the wrong surface shader and renames the newly assigned shader to match the name of the deleted one.

    """
    label = 'Fix | Shading'
    on = 'failedOrWarning'  # The plug-in has been processed, and failed or had a warning
    icon = 'paint.png'

    @staticmethod
    def _transfer_attributes(source_shader: str, target_shader: str):
        """Transfer overridden attributes from source shader to target shader.

        This function transfers overridden attributes from a source shader node to a target shader node,
        excluding any attributes that are specific to either the source or target shader types.

        :param source_shader: The source shader node name
        :param target_shader: The target shader node name
        """

        # Define a dictionary that maps shader types to their corresponding attribute names for diffuse color
        color_attr_mapping = {
            'lambert': 'color',
            'blinn': 'color',
            'phong': 'color',
            'phongE': 'color',
            'standardSurface': 'baseColor',
            # Add more mappings as needed for other shader types
        }

        # Check if transferring diffuse color is required for these shader types
        diffuse_color_transferable = (cmds.nodeType(source_shader) in color_attr_mapping and
                                      cmds.nodeType(target_shader) in color_attr_mapping)

        # List attributes on the source shader
        source_attributes = cmds.listAttr(source_shader, visible=True, settable=True, scalar=True)
        norm_source_attributes = []

        if diffuse_color_transferable:
            # Normalize attribute names to use 'diffuseColor' for diffuse color attributes
            norm_source_attributes[:] = [s.replace(color_attr_mapping.get(cmds.nodeType(source_shader)),
                                                   'diffuseColor') for s in source_attributes]

        if not norm_source_attributes:
            return []  # Return an empty list if no source attributes found

        # List attributes on the target shader
        target_attributes = cmds.listAttr(target_shader, visible=True, settable=True, scalar=True)
        norm_target_attributes = []

        if diffuse_color_transferable:
            # Normalize attribute names to use 'diffuseColor' for diffuse color attributes
            norm_target_attributes[:] = [s.replace(color_attr_mapping.get(cmds.nodeType(target_shader)),
                                                   'diffuseColor') for s in target_attributes]

        if not norm_target_attributes:
            return []  # Return an empty list if no target attributes found

        # Find common attributes between source and target shaders
        common_attributes = list(set(norm_source_attributes).intersection(norm_target_attributes))

        # Map source common attributes back to their original names
        source_common_attributes = [s.replace('diffuseColor',
                                              color_attr_mapping.get(cmds.nodeType(source_shader))) for s in
                                    common_attributes]

        # Detect overridden attributes on the source shader
        overridden_attributes = []
        for attr in source_common_attributes:
            source_value = cmds.getAttr(f"{source_shader}.{attr}")
            default_value = cmds.attributeQuery(attr, node=source_shader, listDefault=True)[0]

            if source_value != default_value:
                overridden_attributes.append(attr)

        # Transfer overridden attributes from source to target
        transferred_attributes = []
        for attr in overridden_attributes:
            value = cmds.getAttr(f"{source_shader}.{attr}")

            if diffuse_color_transferable:
                # Replace attribute name if it's a diffuse color attribute
                attr = attr.replace(color_attr_mapping.get(cmds.nodeType(source_shader)),
                                    color_attr_mapping.get(cmds.nodeType(target_shader)))

            cmds.setAttr(f"{target_shader}.{attr}", value)
            transferred_attributes.append(attr)

        # Check if the source shader has any incoming connections
        incoming_connections = cmds.listConnections(source_shader,
                                                    connections=True,
                                                    destination=False,
                                                    source=True)

        if incoming_connections:
            # Get the source shader connected attribute name
            source_attr_name = incoming_connections[0].split('.')[1]

            # Find the node connected to the source attribute
            connected_node = cmds.listConnections(incoming_connections[1],
                                                  connections=True,
                                                  destination=True,
                                                  source=False)[0]

            # Replace the target's attribute name if it's one of the color attributes
            target_attr_name = source_attr_name.replace(color_attr_mapping.get(cmds.nodeType(source_shader)),
                                                        color_attr_mapping.get(cmds.nodeType(target_shader)))

            # Reconnect the source shader's attribute to the target shader
            cmds.connectAttr(connected_node, f"{target_shader}.{target_attr_name}")

    def process(self, context, plugin):
        """Main method for processing the action

        :param context: The Pyblish context
        :param plugin: The Pyblish plugin
        """
        # Retrieve the list of the keys from plugin.failed_shading_engines_mapping
        failed_shading_engines = list(plugin.failed_shading_engines_mapping.keys())

        # List the failed_shading_engines that are still in the scene
        failed_shading_engines = cmds.ls(failed_shading_engines, long=True)

        # Get required shader types collected in context
        required_shader_type = context.data['required_shader_type']

        # Get excluded nodes collected in context
        excluded_nodes = context.data['excluded_nodes']

        for shading_engine in failed_shading_engines:
            surface_shader = plugin.failed_shading_engines_mapping[shading_engine]

            # Create a shader of the required type
            required_surface_shader = cmds.shadingNode(required_shader_type, asShader=True)

            if surface_shader:
                # Transfer attributes from the failed shader
                self._transfer_attributes(surface_shader, required_surface_shader)

                # Delete surface_shader
                if surface_shader not in excluded_nodes:
                    cmds.delete(surface_shader)

                # Rename the required_surface_shader with surface_shader name
                required_surface_shader = cmds.rename(required_surface_shader, surface_shader)

            # Connect the outColor attribute of the required_surface_shader
            # to the shading engine's surface shader input.
            cmds.connectAttr(f"{required_surface_shader}.outColor", f"{shading_engine}.surfaceShader", force=True)

        # Generate a message about the action result
        result_msg = generate_result_message('hi shape(s) shading issue(s)',
                                             failed_shading_engines,
                                             'fixed')
        # Log the result message
        self.log.info(result_msg)


class ModelHiShadingValidator(pyblish.api.Validator):
    """Model Hi | Shading Validator

    This Pyblish validator plugin checks if all hi shapes have a shader assign, and  whether shading groups assigned to hi shapes have the right type of surface shader(s) connected (specified in the validation data collector).

    If any forbidden surface shaders are found on assigned shading groups, the affected shading groups are considered failed nodes.

    """
    plugin_id = '73a19d36-666a-4ca8-851a-697b3026f142'  # https://www.uuidgenerator.net/version4
    category = 'Model Hi'
    name = 'Shading'

    hosts = ['maya']
    mandatory = False

    label = define_plugin_label(category, name)
    actions = []

    order = pyblish.api.ValidatorOrder + 0.03

    failed_shading_engines_mapping = {}

    @staticmethod
    def _find_unshaded_faces(shape):
        unshaded_faces = []

        # List all faces of the shape
        faces = cmds.polyListComponentConversion(shape, toFace=True)
        # Convert face range to individual faces
        face_components = cmds.filterExpand(faces, selectionMask=34)  # 34 is the face component type
        if not face_components:
            return unshaded_faces

        # Check if any faces have no shading engine assignment
        for face in face_components:
            shading_engine = cmds.listSets(type=1, object=face)  # Type 1 corresponds to shading engines
            if not shading_engine:
                unshaded_faces.append(face)

        return unshaded_faces

    def process(self, context):
        """Main method for processing the current instance

        :param context: (pyblish.api.Context) The Pyblish context used for collecting and publishing data.
        """
        # Retrieve the list of nodes from the instance data
        hi_set_nodes = context.data['hi_set_nodes']

        # Retrieve the list of required shader type from the context
        required_shader_type = context.data['required_shader_type']

        # Retrieve excluded nodes from the context data
        excluded_nodes = context.data['excluded_nodes']

        # Initialize lists to store different types of issues
        hi_shapes_no_shading_engine = []  # A list to store hi shapes with no shading group
        hi_shapes_default_shading_engines = []  # A list to store hi shapes with default shading group
        hi_shapes_unshaded_faces = {}  # A dict to store hi shapes with faces missing a shader

        shading_engine_has_no_surface_shader = []  # A list to store shading engines with no surface shader
        shading_engine_has_default_surface_shader = []  # A list to store shading engines with default surface shader
        shading_engine_has_wrong_surface_shader = []  # A list to store shading engines with the wrong surface shader

        hi_shapes_shading_engines = []  # A list to store shading engines connected to hi shapes

        hi_shapes = cmds.listRelatives(hi_set_nodes, shapes=True, fullPath=True, noIntermediate=True) or []
        # Loop through hi shapes to check for various issues
        for hi_shape in hi_shapes:
            # List shading engines connected to hi shape
            hi_shape_shading_engines = cmds.listConnections(hi_shape, type='shadingEngine')

            # Store hi_shape with no shadingEngine in hi_shapes_no_shading_engine
            if not hi_shape_shading_engines:
                hi_shapes_no_shading_engine.append(hi_shape)
                self.log.warning(f"{hi_shape} has no shading group.")
                continue

            faces_missing_shader = self._find_unshaded_faces(hi_shape)
            if faces_missing_shader:
                hi_shapes_unshaded_faces[hi_shape] = faces_missing_shader

            # Store hi_shape with default shadingEngine in hi_shapes_default_shading_engines
            if any(item in hi_shape_shading_engines for item in excluded_nodes):
                hi_shapes_default_shading_engines.append(hi_shape)
                self.log.warning(f"{hi_shape} has default shading group(s).")

            # Add hi_shape shadingEngines to hi_shapes_shading_engines
            hi_shapes_shading_engines.extend(hi_shape_shading_engines)

        # Actions
        # Add 'select' action classes to the actions list
        if hi_shapes_no_shading_engine:
            select_failed_hi_shapes = actions.create_action_subclass(
                actions.Select,
                'hi shape(s) with no shading group',
                hi_shapes_no_shading_engine
            )
            self.actions.append(select_failed_hi_shapes)

        # Add 'select' action classes to the actions list
        if hi_shapes_unshaded_faces:
            select_failed_hi_shapes = actions.create_action_subclass(
                actions.Select,
                'hi shape(s) with unshaded faces',
                hi_shapes_unshaded_faces.keys()
            )
            self.actions.append(select_failed_hi_shapes)

            face_list = [value for values in hi_shapes_unshaded_faces.values() for value in values]
            select_failed_faces = actions.create_action_subclass(
                actions.Select,
                'face(s) not shaded',
                face_list
            )
            self.actions.append(select_failed_faces)

        # Add 'select' action classes to the actions list
        if hi_shapes_default_shading_engines:
            select_failed_hi_shapes = actions.create_action_subclass(
                actions.Select,
                'hi shape(s) with default shading group(s)',
                hi_shapes_default_shading_engines
            )
            self.actions.append(select_failed_hi_shapes)

        for shading_engine in hi_shapes_shading_engines:
            if shading_engine in excluded_nodes:
                continue

            # Get the surface shader connected to the shading engine
            surface_shader_connection = cmds.listConnections(shading_engine + '.surfaceShader',
                                                             connections=True, source=True, destination=False)

            # Store shading engine in list of corresponding issue and failed_shading_engines_mapping
            if not surface_shader_connection:
                shading_engine_has_no_surface_shader.append(shading_engine)
                self.failed_shading_engines_mapping[shading_engine] = None
                self.log.warning(f"{shading_engine} has no surface shader connected.")
                continue

            # Get the surface shader from surface shader connection
            surface_shader = surface_shader_connection[1]

            # Store shading engine in list of corresponding issue and failed_shading_engines_mapping
            if surface_shader in excluded_nodes:
                shading_engine_has_default_surface_shader.append(shading_engine)
                self.failed_shading_engines_mapping[shading_engine] = surface_shader
                self.log.warning(f"{shading_engine} has a default surface shader.")
                continue

            # Store shading engine in list of corresponding issue and failed_shading_engines_mapping
            if cmds.nodeType(surface_shader) != required_shader_type:
                shading_engine_has_wrong_surface_shader.append(shading_engine)
                self.failed_shading_engines_mapping[shading_engine] = surface_shader
                self.log.warning(f"{shading_engine} has not the required surface shader type."
                                 f"Please use: '{required_shader_type}'")

        # Actions
        # Add 'select' action classes to the actions list
        if shading_engine_has_no_surface_shader:
            select_shading_engines = actions.create_action_subclass(
                actions.Select,
                'shading engine(s) with no surface shader',
                shading_engine_has_no_surface_shader
            )
            self.actions.append(select_shading_engines)

        # Add 'select' action classes to the actions list
        if shading_engine_has_default_surface_shader:
            select_shading_engines = actions.create_action_subclass(
                actions.Select,
                'shading engine(s) with default surface shader',
                shading_engine_has_default_surface_shader
            )
            self.actions.append(select_shading_engines)

        # Add 'select' action classes to the actions list
        if shading_engine_has_wrong_surface_shader:
            select_shading_engines = actions.create_action_subclass(
                actions.Select,
                'shading engine(s) with unrequired surface shader type',
                shading_engine_has_wrong_surface_shader
            )
            self.actions.append(select_shading_engines)

        # Add custom action classes for fixing the issue
        if self.failed_shading_engines_mapping:
            self.actions.append(FixShading)

        # Validate the result and determine if the instance should pass or fail
        validation_result(self, 
                          'hi shape(s) shading assignment issue(s)',
                          hi_shapes_no_shading_engine +
                          list(hi_shapes_unshaded_faces) +
                          hi_shapes_default_shading_engines +
                          list(self.failed_shading_engines_mapping.keys()),
                          self.failure_response)
