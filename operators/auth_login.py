import bpy


class AuthLoginProperties(bpy.types.PropertyGroup):
    """Properties for the login form"""
    username: bpy.props.StringProperty(name="Username")
    password: bpy.props.StringProperty(name="Password", subtype='PASSWORD')


class AuthLoginOperator(bpy.types.Operator):
    """Login to a heat account"""
    bl_idname = "heat.auth_login"
    bl_label = "Login to an account"

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        login_props = context.window_manager.heat_login_properties
        username = login_props.username
        password = login_props.password

        # Perform login logic here, such as checking the username and password against a database.
        # ...

        self.report({'INFO'}, "Successful login")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        login_props = context.window_manager.heat_login_properties
        layout.prop(login_props, "username")
        layout.prop(login_props, "password")

    @classmethod
    def register(cls):
        bpy.utils.register_class(AuthLoginProperties)
        bpy.types.WindowManager.heat_login_properties = bpy.props.PointerProperty(type=AuthLoginProperties)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.heat_login_properties
        bpy.utils.unregister_class(AuthLoginProperties)