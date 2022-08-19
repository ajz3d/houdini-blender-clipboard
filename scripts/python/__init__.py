# coding=utf-8
bl_info = {
    "name": "Houdini-Blender Clipboard",
    "description": "Enables quick geometry interchange between Houdini and Blender.",
    "author": "Artur J. Żarek (ajz3d)",
    "version": (1, 0),
    "blender": (3, 2, 2),
    "location": "File > Import-Export",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/My_Script",
    "tracker_url": "https://developer.blender.org/maniphest/task/edit/form/2/",
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
