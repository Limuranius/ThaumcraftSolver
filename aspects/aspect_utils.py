from .aspects import *
from .recipes import aspect_recipes


def used_in_aspects(aspect: AspectType) -> list[AspectType]:
    result = []
    for other_aspect, recipe in aspect_recipes.items():
        if aspect in recipe:
            result.append(other_aspect)
    return result


def connected_aspects(aspect: AspectType) -> list[AspectType]:
    used_in = used_in_aspects(aspect)
    consists_of = aspect_recipes[aspect]
    return list(set(used_in + consists_of))


def find_shortest_path(start: AspectType, end: AspectType) -> list[AspectType]:
    paths_queue = [[start]]
    while True:
        path = paths_queue.pop(0)
        path_last_aspect = path[-1]
        if path_last_aspect == end:
            return path
        else:
            for aspect in connected_aspects(path_last_aspect):
                new_path = list(path) + [aspect]
                paths_queue.append(new_path)


def find_path(start: AspectType, end: AspectType, length: int) -> list[AspectType]:
    paths_queue = [[start]]
    while len(paths_queue[0]) <= length:
        path = paths_queue.pop(0)
        path_last_aspect = path[-1]
        if path_last_aspect == end and len(path) == length:
            return path
        else:
            for aspect in connected_aspects(path_last_aspect):
                new_path = list(path) + [aspect]
                paths_queue.append(new_path)
    raise Exception("Aspect path not found")


