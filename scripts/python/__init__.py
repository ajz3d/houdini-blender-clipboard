# coding=utf-8
bl_info = {
    "name": "Houdini-Blender Clipboard",
    "description": "Enables quick geometry exchange between Houdini and Blender.",
    "author": "Artur J. Żarek (ajz3d)",
    "version": (1, 0),
    "blender": (3, 2, 2),
    "location": "File > Import-Export",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "https://github.com/ajz3d/houdini-blender-clipboard",
    "tracker_url": "https://github.com/ajz3d/houdini-blender-clipboard/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


from . import blender_manual

def register():
    blender_manual.register()

def unregister():
    blender_manual.unregister()

if __name__ == '__main__':
    register()
