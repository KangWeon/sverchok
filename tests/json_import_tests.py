from sverchok.old_nodes import is_old
from sverchok.utils.testing import *
from sverchok.ui.sv_examples_menu import example_categories_names


class ScriptUvImportTest(SverchokTestCase):

    def test_script_uv_import(self):
        with self.temporary_node_tree("ImportedTree") as new_tree:
            new_tree.sv_process = False
            path = self.get_reference_file_path("script_uv.json")
            importer = JSONImporter.init_from_path(path)
            importer.import_into_tree(new_tree, print_log=False)
            if importer.has_fails:
                raise (ImportError(importer.fail_massage))

            # Check links
            self.assert_nodes_linked("ImportedTree", "Scripted Node Lite", "verts", "UV Connection", "vertices")
            self.assert_nodes_linked("ImportedTree", "UV Connection", "vertices", "Viewer Draw", "Vertices")
            self.assert_nodes_linked("ImportedTree", "UV Connection", "data", "Viewer Draw", "Edges")

            # Check random node properties
            self.assert_node_property_equals("ImportedTree", "UV Connection", "cap_U", False)
            self.assert_node_property_equals("ImportedTree", "UV Connection", "polygons", 'Edges')
            self.assert_node_property_equals("ImportedTree", "UV Connection", "dir_check", 'U_dir')

class ProfileImportTest(SverchokTestCase):

    def test_profile_import(self):
        with self.temporary_node_tree("ImportedTree") as new_tree:
            new_tree.sv_process = False
            importer = JSONImporter.init_from_path(self.get_reference_file_path("profile.json"))
            importer.import_into_tree(new_tree, print_log=False)
            if importer.has_fails:
                raise (ImportError(importer.fail_massage))


class MeshExprImportTest(SverchokTestCase):

    def test_mesh_expr_import(self):
        with self.temporary_node_tree("ImportedTree") as new_tree:
            new_tree.sv_process = False
            importer = JSONImporter.init_from_path(self.get_reference_file_path("mesh.json"))
            importer.import_into_tree(new_tree, print_log=False)
            if importer.has_fails:
                raise (ImportError(importer.fail_massage))

# to keep automated tests from breaking, i've collected a list of examples that need to be skipped
# because they
#  1) require .blend data (greasepencil strokes) or
#  2) 3rd party python modules (mcubes, conway, archicad)

UNITTEST_SKIPLIST = [
    "GreacePencil_injection.json",
    "pointsONface_gather_lines.json",
    "Generative_Art_Lsystem.json",
    # "Genetic_algorithm.blend.json",  # looks like script node is trying to update via import_from_json method
    "Genetic_algorithm_scripted_node.json",
    "Elfnor_topology_nodes.json",
    "l-systems.json",
    "ABCnaming.json",
    "ArchiCAD24import.json",
    "CNC_CUTHOLES_RESIZE.json",
    "Open4d_mesh.json",
    "BIM_ArchiCAD24_import.json",
    "BIM_FreeCAD_import.json",
    "BIM_truss_joint.json",
    "SverchokLogo.json" # Blender 2.90 has a crash in delaunay_2d_cdt on this file :/
]

# @batch_only
class ExamplesImportTest(SverchokTestCase):
    def test_import_examples(self):

        for examples_path, category_name in example_categories_names():

            info("Opening Dir named: %s", category_name)

            examples_set = examples_path / category_name
            for listed_path in examples_set.iterdir():

                # cast from Path class to dumb string.
                path = str(listed_path)

                # assuming these are all jsons for now.
                name = basename(path)

                if name in UNITTEST_SKIPLIST:
                    info(f"Skipping test import of: {name} - to permit unit-tests to continue")
                    continue

                with self.subTest(file=name):
                    # info("Importing: %s", name)
                    with self.temporary_node_tree("ImportedTree") as new_tree:
                        # Do not try to process imported tree,
                        # that will just take time anyway
                        new_tree.sv_process = False
                        importer = JSONImporter.init_from_path(path)
                        importer.import_into_tree(new_tree, print_log=False)
                        for node in new_tree.nodes:
                            if is_old(node):
                                error_format = "This example contains deprecated node `{}' ({}). Please upgrade the example file."
                                self.fail(error_format.format(node.name, node.bl_idname))
                            if getattr(node, 'missing_dependency', False):
                                self.skipTest("Some dependencies was not installed")
                        if importer.has_fails:
                            raise ImportError(importer.fail_massage)
