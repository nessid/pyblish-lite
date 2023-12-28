import pyblish.api
from pyblish_core.plugins_utilities.result_by_plugin_type import collection_result
from pyblish_core.plugins_utilities.strings_handling import define_plugin_label


class ValidationContextCollector(pyblish.api.Collector):
    """Collect Validation Context Data

    This collector gathers contextual data necessary for validation.

    """
    plugin_id = 'a379a460-6d21-49ce-9c75-ad4e202b17dd'  # https://www.uuidgenerator.net/version4
    category = 'Data'
    name = 'Validation context'

    hosts = ['maya']
    mandatory = True

    label = define_plugin_label(category, name)
    settings = 'default'  # This value can be overriden with filtering: https://learn.pyblish.com/24-filtering

    def _collect_required_shader(self, context):
        """Collect Required Shader Types

        This method collects required shader types and stores them in the Pyblish context data.
        These shader types are used as reference for validation.

        :param context: The Pyblish context.
        """
        # List allowed shader types
        required_shader_types_mapping = {
            'default': 'standardSurface',
            'modeling': 'blinn'
        }

        # Store nodes in the context data
        context.data['required_shader_type'] = required_shader_types_mapping[self.settings]

        # Log the collection result
        collection_result(self, 'required shader type(s)', required_shader_types_mapping[self.settings])

        return required_shader_types_mapping[self.settings]

    def _collect_root_nodes_rules(self, context):
        """Collect Required Root Nodes

        This method collects required and valid root nodes and stores them in the Pyblish context data.
        These root nodes represent the required top-level nodes in the scene.

        :param context: The Pyblish context.
        """
        # List of root node patterns formatted for regular expressions
        required_root_nodes = ['GEO']
        valid_root_nodes = ['.*TRASH', '.*HELP']

        # Store lists in the context data
        context.data['required_root_nodes'] = required_root_nodes
        context.data['valid_root_nodes'] = valid_root_nodes

        # Log the collection result
        collection_result(self, 'required root node(s)', required_root_nodes)
        collection_result(self, 'valid root node(s)', valid_root_nodes)

        return required_root_nodes + valid_root_nodes

    def _collect_lod_types(self, context):
        """Collect LOD Types

        This method collects LOD types and stores them in the Pyblish context data.

        :param context: The Pyblish context.
        """
        lod_types = ['hi', 'lo', 'viz']

        # Store nodes in the context data
        context.data['lod_types'] = lod_types

        # Log the collection result
        collection_result(self, 'valid LOD type(s)', lod_types)

        return lod_types

    def _collect_shape_types_abbreviations(self, context):
        """Collect Shape Types Abbreviations

        This method collects shape types abbreviations and stores them in the Pyblish context data.

        :param context: The Pyblish context.
        """
        # Map shape types with their associated abbreviations
        shapes_abbr_mapping = {
            'mesh': 'msh',
            'nurbsCurve': 'crv',
            'nurbsSurface': 'srf',
            'follicle': 'flc'
        }

        # Store nodes in the context data
        context.data['shapes_abbr_mapping'] = shapes_abbr_mapping

        # Log the collection result
        collection_result(self, 'shape type(s) with associated abbreviation', shapes_abbr_mapping)

        return list(shapes_abbr_mapping.values()) + list(shapes_abbr_mapping.keys())

    def _collect_shading_affix_mapping(self, context):
        """Collect Shading Nodes Affixes

        This method collects shading nodes affixes and stores them in the Pyblish context data.

        :param context: The Pyblish context.
        """
        # Map shape types with their associated abbreviations
        shading_affix_mapping = {
            'shadingEngine': 'SG',
            'surfaceShader': 'SHD',
        }

        # Store nodes in the context data
        context.data['shading_affix_mapping'] = shading_affix_mapping

        # Log the collection result
        collection_result(self, 'shading node(s) with associated affix', shading_affix_mapping)

        return list(shading_affix_mapping.values()) + list(shading_affix_mapping.keys())

    def _collect_group_suffix(self, context):
        """Collect Group Suffix

        This method collects the group suffix and stores it in the Pyblish context data.

        :param context: The Pyblish context.
        """
        group_suffix = 'grp'

        # Store nodes in the context data
        context.data['group_suffix'] = group_suffix

        # Log the collection result
        collection_result(self, 'group suffix(es)', group_suffix)

        return group_suffix

    def process(self, context):
        """Main method for processing the current context.

        :param context: The Pyblish context used for collecting and publishing data.
        """
        # Reserved patterns are patterns that can't be used in basename.
        reserved_patterns = []

        reserved_patterns.extend(self._collect_root_nodes_rules(context))
        reserved_patterns.extend(self._collect_lod_types(context))
        reserved_patterns.extend(self._collect_shape_types_abbreviations(context))
        reserved_patterns.extend(self._collect_shading_affix_mapping(context))

        reserved_patterns.append(self._collect_required_shader(context))
        reserved_patterns.append(self._collect_group_suffix(context))

        context.data['reserved_patterns'] = reserved_patterns

        # Log the collection result
        collection_result(self, 'reserved pattern(s)', reserved_patterns, 100)
