import bpy
import os

bl_info = {
    "name": "PBR Importer",
    "author": "ClassOutside",
    "version": (1, 0),
    "blender": (4, 1, 1),
    "description": "Assists with adding PBRs in Blender",
    "category": "Shader Editing",
}

class ImportPBRsOperator(bpy.types.Operator):
    bl_idname = "object.import_pbrs_operator"
    bl_label = "Import PBRs"

    def import_metallic(self, materials_dir):
        for file in os.listdir(materials_dir):
            if 'metallic' in file.lower() and file.endswith('.png'):
                metallic_file = os.path.join(materials_dir, file)
                break
        else:
            self.report({'WARNING'}, "No metallic .png file found")
            return

        bpy.ops.node.add_node(type="ShaderNodeTexImage", use_transform=True)
        image_texture_node = bpy.context.active_node
        image_texture_node.image = bpy.data.images.load(metallic_file)
        image_texture_node.image.colorspace_settings.name = 'Non-Color'

        principled_bsdf_node = next((node for node in bpy.context.active_object.active_material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if not principled_bsdf_node:
            self.report({'WARNING'}, "No Principled BSDF node found")
            return

        bpy.context.active_object.active_material.node_tree.links.new(image_texture_node.outputs['Color'], principled_bsdf_node.inputs['Metallic'])

    # Import smoothness map and invert to represent roughness
    def import_roughness(self, materials_dir):
        for file in os.listdir(materials_dir):
            if 'smoothness' in file.lower() and file.endswith('.png'):
                smoothness_file = os.path.join(materials_dir, file)
                break
        else:
            self.report({'WARNING'}, "No smoothness .png file found")
            return

        bpy.ops.node.add_node(type="ShaderNodeTexImage", use_transform=True)
        image_texture_node = bpy.context.active_node
        image_texture_node.image = bpy.data.images.load(smoothness_file)

        bpy.ops.node.add_node(type="ShaderNodeInvert", use_transform=True)
        invert_node = bpy.context.active_node
        invert_node.inputs['Fac'].default_value = 1

        bpy.context.active_object.active_material.node_tree.links.new(image_texture_node.outputs['Color'], invert_node.inputs['Color'])

        principled_bsdf_node = next((node for node in bpy.context.active_object.active_material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if not principled_bsdf_node:
            self.report({'WARNING'}, "No Principled BSDF node found")
            return

        bpy.context.active_object.active_material.node_tree.links.new(invert_node.outputs['Color'], principled_bsdf_node.inputs['Roughness'])

    # Import ambient occlusion map and mix with diffuse.
    def import_ambientOcclusion(self, materials_dir):
        for file in os.listdir(materials_dir):
            if '_ao' in file.lower() and file.endswith('.png'):
                ao_file = os.path.join(materials_dir, file)
                break
        else:
            self.report({'WARNING'}, "No _ao .png file found")
            return

        bpy.ops.node.add_node(type="ShaderNodeTexImage", use_transform=True)
        image_texture_node = bpy.context.active_node
        image_texture_node.image = bpy.data.images.load(ao_file)
        image_texture_node.image.colorspace_settings.name = 'Non-Color'

        bpy.ops.node.add_node(type="ShaderNodeInvert", use_transform=True)
        invert_node = bpy.context.active_node
        invert_node.inputs['Fac'].default_value = 0.217

        bpy.context.active_object.active_material.node_tree.links.new(image_texture_node.outputs['Color'], invert_node.inputs['Color'])

        bpy.ops.node.add_node(type="ShaderNodeMixRGB", use_transform=True)
        mix_node = bpy.context.active_node
        mix_node.blend_type = 'MULTIPLY'
        mix_node.use_clamp = False

        bpy.context.active_object.active_material.node_tree.links.new(invert_node.outputs['Color'], mix_node.inputs['Color1'])

        principled_bsdf_node = next((node for node in bpy.context.active_object.active_material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if not principled_bsdf_node:
            self.report({'WARNING'}, "No Principled BSDF node found")
            return

        base_color_texture_node = next((link.from_node for link in principled_bsdf_node.inputs['Base Color'].links if link.from_node.type == 'TEX_IMAGE'), None)
        if not base_color_texture_node:
            self.report({'WARNING'}, "No image texture node found connected to the 'Base Color' input")
            return

        bpy.context.active_object.active_material.node_tree.links.new(base_color_texture_node.outputs['Color'], mix_node.inputs['Color2'])

        bpy.context.active_object.active_material.node_tree.links.new(mix_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])

        mix_node.inputs['Fac'].default_value = 1

    def import_normal(self, materials_dir):
        principled_bsdf_node = next((node for node in bpy.context.active_object.active_material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if not principled_bsdf_node:
            self.report({'WARNING'}, "No Principled BSDF node found")
            return

        if not principled_bsdf_node.inputs['Normal'].is_linked:
            for file in os.listdir(materials_dir):
                if 'normal' in file.lower() and file.endswith('.png'):
                    normal_file = os.path.join(materials_dir, file)
                    break
            else:
                self.report({'WARNING'}, "No normal .png file found")
                return

            bpy.ops.node.add_node(type="ShaderNodeNormalMap", use_transform=True)
            normal_map_node = bpy.context.active_node

            bpy.ops.node.add_node(type="ShaderNodeTexImage", use_transform=True)
            image_texture_node = bpy.context.active_node
            image_texture_node.image = bpy.data.images.load(normal_file)
            image_texture_node.image.colorspace_settings.name = 'Non-Color'

            bpy.context.active_object.active_material.node_tree.links.new(image_texture_node.outputs['Color'], normal_map_node.inputs['Color'])
            bpy.context.active_object.active_material.node_tree.links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])

    def execute(self, context):
        blend_dir = bpy.path.abspath("//")
        materials_dir = os.path.join(blend_dir, "materials")
        if not os.path.exists(materials_dir):
            self.report({'WARNING'}, "No materials folder found")
            return {'CANCELLED'}

        self.import_metallic(materials_dir)
        self.import_roughness(materials_dir)
        self.import_ambientOcclusion(materials_dir)
        self.import_normal(materials_dir)
        return {'FINISHED'}

def draw_func(self, context):
    layout = self.layout
    layout.operator("object.import_pbrs_operator", text="Import PBRs")

def register():
    bpy.utils.register_class(ImportPBRsOperator)
    bpy.types.NODE_MT_context_menu.append(draw_func)

def unregister():
    bpy.types.NODE_MT_context_menu.remove(draw_func)
    bpy.utils.unregister_class(ImportPBRsOperator)

if __name__ == "__main__":
    register()
