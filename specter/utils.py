def get_fullname(obj):
    obj_type = obj

    if not isinstance(obj, type):
        obj_type = type(obj)

    return f'{obj_type.__module__}.{obj_type.__name__}'
