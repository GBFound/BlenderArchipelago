import bpy
from . import redraw


# CollectionProperty accepts PropertyGroup but not StringProperty
class Message(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty()


class AP_UL_Messages(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.text)


def add_message(text: str):
    messages = bpy.context.scene.ap_messages
    message = messages.add()
    message.text = text
    messages.move(len(messages) - 1, 0)
    bpy.context.scene.ap_messages_index = 0
    redraw.schedule_redraw_panels()


def register():
    bpy.types.Scene.ap_messages = bpy.props.CollectionProperty(type=Message)
    bpy.types.Scene.ap_messages_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Scene.ap_messages_index
    del bpy.types.Scene.ap_messages
