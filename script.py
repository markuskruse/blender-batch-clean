import bpy
import bmesh

def edit():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.reveal()


def unedit():
    bpy.ops.object.mode_set(mode='OBJECT')


def triangulate():
    #triangulate
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')


def delete_loose():
    #delete loose
    bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=True)


def delete_interior():
    #delete interior
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_interior_faces()
    bpy.ops.mesh.delete(type='FACE')


def remove_doubles(threshold):
    #merge doubles
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)


def dissolve_degenerate(threshold):
    #dissolve degenerate
    bpy.ops.mesh.dissolve_degenerate(threshold=threshold)


def fix_non_manifold(bm):
    total_non_manifold = count_non_manifold_verts(bm)

    if not total_non_manifold:
        return

    bm_states = set()
    bm_key = elem_count(bm)
    bm_states.add(bm_key)

    while True:
        fill_non_manifold()
        delete_newly_generated_non_manifold_verts()

        bm_key = elem_count(bm)
        if bm_key in bm_states:
            break
        else:
            bm_states.add(bm_key)


def delete_newly_generated_non_manifold_verts():
    """delete any newly generated vertices from the filling repair"""
    select_non_manifold_verts(use_wire=True, use_verts=True)
    bpy.ops.mesh.delete(type='VERT')


def fill_non_manifold():
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.fill_holes(sides=0)


def make_normals_consistently_outwards():            
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()


def count_non_manifold_verts(bm):
    """return a set of coordinates of non-manifold vertices"""
    select_non_manifold_verts(use_wire=True, use_boundary=True, use_verts=True)
    return sum((1 for v in bm.verts if v.select))


def select_non_manifold_verts(
    use_wire=False,
    use_boundary=False,
    use_multi_face=False,
    use_non_contiguous=False,
    use_verts=False,
):
    """select non-manifold vertices"""
    bpy.ops.mesh.select_non_manifold(
        extend=False,
        use_wire=use_wire,
        use_boundary=use_boundary,
        use_multi_face=use_multi_face,
        use_non_contiguous=use_non_contiguous,
        use_verts=use_verts,
    )


def elem_count(bm):
    return len(bm.verts), len(bm.edges), len(bm.faces) 

def clean(obj):
    bpy.context.view_layer.objects.active = obj

    edit()

    bm = bmesh.from_edit_mesh(obj.data)

    bm_key_orig = elem_count(bm)

    triangulate()
    delete_loose()
    delete_interior()
    remove_doubles(0.001)
    dissolve_degenerate(0.001)
    fix_non_manifold(bm)
    make_normals_consistently_outwards()

    bm_key = elem_count(bm)

    unedit()

    verts = bm_key[0] - bm_key_orig[0]
    edges = bm_key[1] - bm_key_orig[1]
    faces = bm_key[2] - bm_key_orig[2]

    print(("Modified: {:+} vertices, {:+} edges, {:+} faces").format(verts, edges, faces))


sel_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')

for obj in sel_objs:
    print(obj.name)
    clean(obj)

