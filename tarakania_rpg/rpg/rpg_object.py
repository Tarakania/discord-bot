from __future__ import annotations

from typing import Any, Dict, List, Type, Iterator, TypeVar, Tuple

from yaml import safe_load

from constants import DATA_DIR


TRPGObject = TypeVar("TRPGObject", bound="RPGObject")


class UnknownObject(Exception):
    pass


class _RPGOBjectMeta(type):
    def __new__(
        mcls, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]
    ) -> type:
        cls = super().__new__(mcls, name, bases, dct)

        setattr(cls, "_storage_by_id", {})
        setattr(cls, "_storage_by_name", {})

        for base in bases:
            base._subclasses.append(cls)  # type: ignore

        return cls


class RPGObject(metaclass=_RPGOBjectMeta):
    config_filename = ""
    config_folder = ""

    _subclasses: List[RPGObject] = []

    __slots__ = ("id", "name", "_storage_by_id", "_storage_by_name")

    def __init__(self, **kwargs: Any):
        self._storage_by_id: Dict[int, TRPGObject]  # type: ignore
        self._storage_by_name: Dict[str, TRPGObject]  # type: ignore

        self.id: int = kwargs.pop("id")
        self.name: str = kwargs.pop("name")

        if kwargs:
            raise ValueError(
                f"Unknown kwarg(s) passed for {type(self)}: {tuple(kwargs.keys())}"
            )

        self._storage_by_id[self.id] = self
        self._storage_by_name[self.name.lower()] = self

    @classmethod
    def from_data(cls: Type[TRPGObject], data: Dict[str, Any]) -> TRPGObject:
        return cls(**data)

    @staticmethod
    def _read_objects_from_file(cls: Type[TRPGObject]) -> Dict[int, Any]:
        with open(
            f"{DATA_DIR}/rpg/{cls.config_folder}{cls.config_filename}"
        ) as f:
            data = safe_load(f)

        if data is None:  # empty config
            return {}

        for k, v in data.items():
            v["id"] = k

        return data

    @staticmethod
    def _load_objects_from_file(cls: Type[TRPGObject]) -> List[TRPGObject]:
        all_data = cls._read_objects_from_file(cls)

        created = []

        for id, data in all_data.items():
            new_item = cls.from_data(data)

            created.append(new_item)

        return created

    @staticmethod
    def _drop_objects(cls: Type[RPGObject]) -> None:
        cls._storage_by_id = {}
        cls._storage_by_name = {}

    @classmethod
    def from_id(cls, id: int) -> TRPGObject:
        if not cls._subclasses:
            try:
                return cls._storage_by_id[id]
            except KeyError:
                raise UnknownObject

        for subclass in cls._subclasses:
            instance = subclass._storage_by_id.get(id)
            if instance is not None:
                return instance

        raise UnknownObject

    @classmethod
    def from_name(cls, name: str) -> TRPGObject:
        if not cls._subclasses:
            try:
                return cls._storage_by_name[name]
            except KeyError:
                raise UnknownObject

        for subclass in cls._subclasses:
            instance = subclass._storage_by_name.get(name)
            if instance is not None:
                return instance

        raise UnknownObject

    def __str__(self) -> str:
        return f"{self.name}[{self.id}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"


def all_instances(cls: Type[TRPGObject]) -> Iterator[TRPGObject]:
    yield from cls._storage_by_id.values()
