from pyblish_plugins.pyblish_plugins_maya.core.mesh_validators import (
    validate_mesh_border_edges,
    validate_mesh_empty,
    validate_mesh_holed_faces,
    validate_mesh_invalid_vertices,
    validate_mesh_lamina_faces,
    validate_mesh_ngons,
    validate_mesh_non_manifold,
    validate_mesh_starlike,
    validate_mesh_triangles,
    validate_mesh_zero_edge_length,
    # validate_mesh_unfrozen_vertices
)


def create_subclass(superclass, _lod_type: str, _order_offset: float):
    class Subclass(superclass):
        plugin_id = superclass.plugin_id + _lod_type
        category = f"{superclass.category} {_lod_type.capitalize()}"

        label = category + ' | ' + superclass.name
        order = superclass.order + _order_offset
        families = [f"model_{_lod_type}_nodes"]

        actions = []

    Subclass.__name__ = f"{_lod_type.capitalize()}_{superclass.__name__}"
    Subclass.__doc__ = _lod_type.capitalize() + ' ' + superclass.__doc__
    # print(f"Create {Subclass.__name__}")
    return Subclass


def create_mesh_subclasses():
    validator_classes = [
        validate_mesh_border_edges.MeshBorderEdgesValidator,
        validate_mesh_empty.MeshEmptyValidator,
        validate_mesh_holed_faces.MeshHoleFacesValidator,
        validate_mesh_invalid_vertices.MeshInvalidVerticesValidator,
        validate_mesh_lamina_faces.MeshLaminaFacesValidator,
        validate_mesh_ngons.MeshNgonsValidator,
        validate_mesh_non_manifold.MeshNonManifoldValidator,
        validate_mesh_starlike.StarLikeVerticesValidator,
        validate_mesh_triangles.MeshTrianglesValidator,
        validate_mesh_zero_edge_length.MeshZeroEdgeLengthValidator,
        # Add more validator classes as needed
    ]
    order_offset_mapping = {'hi': 0.05, 'lo': 0.051, 'viz': 0.052}
    for lod_type in ['hi', 'lo', 'viz']:
        order_offset = order_offset_mapping[lod_type]
        for validator_class in validator_classes:
            subclass = create_subclass(validator_class, lod_type, order_offset)
            subclass_name = f"validate_{lod_type.capitalize()}_{validator_class.__name__}"
            globals()[subclass_name] = subclass


create_mesh_subclasses()
