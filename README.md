# PBR-Importer
Blender add-on to assist with importing PBRs

# Use
1. Install the add-on in Blender
2. Prepare a folder named 'materials' in the same directory as your blender file.
3. Prepare any or all of the following images to be imported:
    - Normal
    - Metallic
    - Smoothness
    - Ambient Occlusion
5. The images must all be .png
6. The image names must include the following words:
    - Normal must include 'normal'
    - Metallic must include 'metallic'
    - Smoothness must include 'smoothness'
    - Ambient occlusion must include 'ao'
8. In blender, open the shader editor to the material you want to import PBR images for.
9. Right click the Principled BSDF shader.
10. Select the option 'Import PBRs'

After a moment the textures should be loaded and connected to the principled BSDF shader.
