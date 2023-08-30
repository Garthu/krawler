import dataclasses

def fromDataclassesToDict(objects):
    return [dataclasses.asdict(object_) for object_ in objects]
