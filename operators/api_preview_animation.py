import bpy
import os


def get_addon_thumbnail_path(name):
    script_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_path, f"..{os.sep}assets")
    # fpath = os.path.join(p, subpath)
    ext = name.split('.')[-1]
    next = ''
    if not (ext == 'jpg' or ext == 'png'):  # already has ext?
        next = '.jpg'
    subpath = f"img{os.sep}{name}{next}"
    return os.path.join(script_path, subpath)


def img_to_preview(img, copy_original=False):
    if bpy.app.version[0] >= 3:
        img.preview_ensure()
    if not copy_original:
        return
    # if img.preview.image_size != img.size:
    #     img.preview.image_size = (img.size[0], img.size[1])
    #     img.preview.image_pixels_float = img.pixels[:]



class APIPreviewOperator(bpy.types.Operator):
    """A preview of the currently selected Heat animation"""
    bl_idname = "heat.api_preview_animation"
    bl_label = "Preview selected Heat animation"

    def execute(self, context):
        context.scene.frame_set(1)
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def draw(self, context):
        layout = self.layout

        tpath = get_addon_thumbnail_path('dummy.png')
        img = bpy.data.images.load(tpath, check_existing = True)
        preview = img.preview_ensure()

        layout.label(text="heat preview")
        layout.template_icon(icon_value=preview.icon_id, scale=7.0)

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
