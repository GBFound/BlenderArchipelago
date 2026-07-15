from . import auto_load

auto_load.init()


def register():
    auto_load.register()
    print("\n[Blender AP] Registered.")


def unregister():
    auto_load.unregister()
    print("[Blender AP] Unregistered.")
