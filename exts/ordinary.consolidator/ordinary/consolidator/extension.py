import omni.ext
import omni.ui as ui
from pxr import Usd, Sdf, Gf, UsdGeom, UsdShade
from .MeshMaker import MeshMaker


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class OrdinaryMeshConsolidatorExtension(omni.ext.IExt):

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        self._window = ui.Window("Mesh Consolidator", width=300, height=300)
        with self._window.frame:

            # TODO: Clean up the UI... one day.
            with ui.VStack():

                def on_click():
                    self.consolidate_prim()

                with ui.HStack():
                    ui.Button("Consolidate", clicked_fn=on_click)


    # The main body of the clean up code for VRoid Studio characters.
    def consolidate_prim(self):

        ctx = omni.usd.get_context()
        stage = ctx.get_stage()

        selections = ctx.get_selection().get_selected_prim_paths()

        # Patch the skeleton structure, if not done already. Add "Root" to the joint list.
        for prim_path in selections:
            mesh_prim = stage.GetPrimAtPath(prim_path)
            if mesh_prim and mesh_prim.IsA(UsdGeom.Mesh):
                mesh: UsdGeom.Mesh = UsdGeom.Mesh(mesh_prim)
                self.perform_consolidation(stage, mesh, prim_path + "_consolidated")


    def perform_consolidation(self, stage: Usd.Stage, old_mesh: UsdGeom.Mesh, new_mesh_path):

        faceVertexIndices = old_mesh.GetFaceVertexIndicesAttr().Get()
        faceVertexCounts = old_mesh.GetFaceVertexCountsAttr().Get()
        points = old_mesh.GetPointsAttr().Get()
        normals = old_mesh.GetNormalsAttr().Get()
        normalsInterpolation = UsdGeom.Primvar(old_mesh.GetNormalsAttr()).GetInterpolation()
        stAttr = old_mesh.GetPrim().GetAttribute('primvars:st0')
        stInterpolation = UsdGeom.Primvar(stAttr).GetInterpolation()
        st = stAttr.Get()
        material = UsdShade.MaterialBindingAPI(old_mesh.GetPrim()).GetDirectBindingRel().GetTargets()

        new_mesh = MeshMaker(stage, material)

        # Assumes faceVertexCounts are all '3'
        for face_index in range(len(faceVertexIndices) // 3):

            pi1 = faceVertexIndices[face_index * 3 + 0]
            pi2 = faceVertexIndices[face_index * 3 + 1]
            pi3 = faceVertexIndices[face_index * 3 + 2]

            p1 = points[pi1]
            p2 = points[pi2]
            p3 = points[pi3]

            if normalsInterpolation == UsdGeom.Tokens.faceVarying:
                n1 = normals[face_index * 3 + 0]
                n2 = normals[face_index * 3 + 1]
                n3 = normals[face_index * 3 + 2]
            else:
                n1 = normals[pi1]
                n2 = normals[pi2]
                n3 = normals[pi3]

            if stInterpolation == UsdGeom.Tokens.faceVarying:
                st1 = st[face_index * 3 + 0]
                st2 = st[face_index * 3 + 1]
                st3 = st[face_index * 3 + 2]
            else:
                st1 = st[pi1]
                st2 = st[pi2]
                st3 = st[pi3]

            new_mesh.add_face(p1, p2, p3, n1, n2, n3, st1, st2, st3)

        new_mesh.create_at_path(new_mesh_path)
    
