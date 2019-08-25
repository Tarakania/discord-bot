from .race import Race
from .items import load_all_items
from .class_ import Class
from .location import Location


def load_races() -> None:
    Race._load_objects_from_file(Race)


def load_classes() -> None:
    Class._load_objects_from_file(Class)


def load_locations() -> None:
    Location._load_objects_from_file(Location)


def load_objects() -> None:
    load_races()
    load_classes()
    load_locations()

    load_all_items()
