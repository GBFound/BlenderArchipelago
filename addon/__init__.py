from . import auto_load

auto_load.init()


def register():
    auto_load.register()
    print("\n[Archipelago] Registered.")


def unregister():
    auto_load.unregister()
    print("[Archipelago] Unregistered.")
