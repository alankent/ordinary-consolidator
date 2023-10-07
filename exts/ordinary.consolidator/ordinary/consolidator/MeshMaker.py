from pxr import Usd, Sdf, Gf, UsdGeom, UsdShade, UsdSkel


# This class creates a new Mesh by adding faces one at a time.
# When don, you ask it to create a new Mesh prim.
class MeshMaker:

    def __init__(self, stage: Usd.Stage, material):
        self.stage = stage
        self.material = material
        self.faceVertexCounts = []
        self.faceVertexIndices = []
        self.normals = []
        self.st = []
        self.points = []

    # Create a Mesh prim at the given prim path.
    def create_at_path(self, prim_path) -> UsdGeom.Mesh:
        # https://stackoverflow.com/questions/74462822/python-for-usd-map-a-texture-on-a-cube-so-every-face-have-the-same-image
        mesh: UsdGeom.Mesh = UsdGeom.Mesh.Define(self.stage, prim_path)
        mesh.CreateSubdivisionSchemeAttr().Set(UsdGeom.Tokens.none)
        mesh.CreatePointsAttr(self.points)
        mesh.CreateExtentAttr(UsdGeom.PointBased(mesh).ComputeExtent(mesh.GetPointsAttr().Get()))
        mesh.CreateNormalsAttr(self.normals)
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
        mesh.CreateFaceVertexCountsAttr(self.faceVertexCounts)
        mesh.CreateFaceVertexIndicesAttr(self.faceVertexIndices)
        UsdGeom.PrimvarsAPI(mesh.GetPrim()).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying).Set(self.st)
        UsdShade.MaterialBindingAPI(mesh).GetDirectBindingRel().SetTargets(self.material)
        return mesh
    
    # Add a new face (3 points with normals and mappings to part of the texture)
    def add_face(self, p1, p2, p3, normal1, normal2, normal3, st1, st2, st3):
        self.faceVertexCounts.append(3)
        self.faceVertexIndices.append(self.add_point(p1))
        self.faceVertexIndices.append(self.add_point(p2))
        self.faceVertexIndices.append(self.add_point(p3))
        self.normals.append(normal1)
        self.normals.append(normal2)
        self.normals.append(normal3)
        self.st.append(st1)
        self.st.append(st2)
        self.st.append(st3)

    # Given a point, find an existing points array entry and return its index, otherwise add another point
    # and return the index of the new point.
    def add_point(self, point):

        for i in range(0, len(self.points)):
            if self.points[i] == point:
                return i

        self.points.append(point)

        return len(self.points) - 1
    
