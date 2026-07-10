from pathlib import Path
import xml.etree.ElementTree as ET

folder = Path(
    "/home/jghantou/codes/hgo_biomechanical_cardiac_model/"
    "res/2D_case_MPI/Test_horizontal_forces_disks_With_dirichlet/"
    "Direct/plots/case2/ref_mesh"
)

vtu_files = sorted(folder.glob("*.vtu"))
output = folder / "partition_2d.pvtu"

if not vtu_files:
    raise RuntimeError("No .vtu files were found in this folder.")

first = vtu_files[0]
tree = ET.parse(first)
root = tree.getroot()

ug = root.find("UnstructuredGrid")
if ug is None:
    raise RuntimeError("No <UnstructuredGrid> element was found.")

piece = ug.find("Piece")
if piece is None:
    raise RuntimeError("No <Piece> element was found.")

pvtu = ET.Element(
    "VTKFile",
    {
        "type": "PUnstructuredGrid",
        "version": root.attrib.get("version", "0.1"),
        "byte_order": root.attrib.get("byte_order", "LittleEndian"),
    },
)

if "header_type" in root.attrib:
    pvtu.set("header_type", root.attrib["header_type"])

pug = ET.SubElement(
    pvtu,
    "PUnstructuredGrid",
    {"GhostLevel": "0"}
)


def add_parallel_data(src_name, dst_name):
    src = piece.find(src_name)
    if src is None:
        return

    dst = ET.SubElement(pug, dst_name, src.attrib)

    for da in src.findall("DataArray"):
        attrs = {}

        for key in ["type", "Name", "NumberOfComponents"]:
            if key in da.attrib:
                attrs[key] = da.attrib[key]

        ET.SubElement(dst, "PDataArray", attrs)


add_parallel_data("PointData", "PPointData")
add_parallel_data("CellData", "PCellData")

points = piece.find("Points")
if points is None:
    raise RuntimeError("No <Points> element was found.")

point_array = points.find("DataArray")
if point_array is None:
    raise RuntimeError("No <DataArray> element was found inside <Points>.")

ppoints = ET.SubElement(pug, "PPoints")

point_attrs = {}

for key in ["type", "NumberOfComponents"]:
    if key in point_array.attrib:
        point_attrs[key] = point_array.attrib[key]

if "NumberOfComponents" not in point_attrs:
    point_attrs["NumberOfComponents"] = "3"

ET.SubElement(ppoints, "PDataArray", point_attrs)

for file in vtu_files:
    ET.SubElement(
        pug,
        "Piece",
        {"Source": file.name}
    )

ET.indent(pvtu, space="  ")

ET.ElementTree(pvtu).write(
    output,
    encoding="utf-8",
    xml_declaration=True
)

print(f"Created: {output}")
print("Included files:")

for file in vtu_files:
    print(" -", file.name)