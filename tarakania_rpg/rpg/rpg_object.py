from __future__ import annotations

from logging import getLogger
from contextlib import suppress
from typing import Any, Dict, List, Type, Iterator, TypeVar, Tuple

from yaml import safe_load

from constants import DATA_DIR


log = getLogger("object_loader")

TRPGObject = TypeVar("TRPGObject", bound="RPGObject")

_subclasses: Dict[type, List[Type[RPGObject]]] = {}


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
            if base not in _subclasses:
                _subclasses[base] = []

            _subclasses[base].append(cls)

        return cls


class RPGObject(metaclass=_RPGOBjectMeta):
    config_filename = ""
    config_folder = ""

    __slots__ = ("id", "name", "_storage_by_id", "_storage_by_name")

    def __init__(self, **kwargs: Any):
        self._storage_by_id: Dict[int, TRPGObject]  # type: ignore
        self._storage_by_name: Dict[str, TRPGObject]  # type: ignore

        self._subclasses: List[RPGObject]

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
            f"{DATA_DIR}/rpg/{cls.config_folder}{cls.config_filename}", encoding='utf8'
        ) as f:
            data = safe_load(f)

        if data is None:  # empty config
            return {}

        for k, v in data.items():
            v["id"] = k

        return data

    @staticmethod
    def _load_objects_from_file(cls: Type[TRPGObject]) -> List[TRPGObject]:
        log.debug(f"Loading {cls.__name__} objects")

        all_data = cls._read_objects_from_file(cls)

        created = []

        for id, data in all_data.items():
            new_item = cls.from_data(data)

            created.append(new_item)

        return created

    @staticmethod
    def _drop_objects(cls: Type[RPGObject]) -> None:
        log.debug(f"Dropping {cls.__name__} objects")

        cls._storage_by_id = {}
        cls._storage_by_name = {}

    @classmethod
    def from_id(cls, id: int) -> TRPGObject:
        subclasses = _subclasses.get(cls)
        if subclasses is None:
            try:
                return cls._storage_by_id[id]
            except KeyError:
                raise UnknownObject

        for subclass in subclasses:
            with suppress(UnknownObject):
                return subclass.from_id(id)

        raise UnknownObject

    @classmethod
    def from_name(cls, name: str) -> TRPGObject:
        subclasses = _subclasses.get(cls)
        if subclasses is None:
            try:
                return cls._storage_by_name[name]
            except KeyError:
                raise UnknownObject

        for subclass in subclasses:
            with suppress(UnknownObject):
                return subclass.from_name(name)

        raise UnknownObject

    @classmethod
    def all_instances(cls) -> Iterator[RPGObject]:
        subclasses = _subclasses.get(cls)
        if subclasses is None:
            yield from cls._storage_by_id.values()

            return

        for subclass in subclasses:
            yield from subclass.all_instances()

    def __str__(self) -> str:
        return f"{self.name}[{self.id}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
