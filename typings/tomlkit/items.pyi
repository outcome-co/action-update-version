from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar, Dict, Generator, Optional, Tuple, Type, Union

from tomlkit.container import Container

class KeyType(Enum):
    Bare: ClassVar[str]
    Basic: ClassVar[str]
    Literal: ClassVar[str]

class Key:
    key: str
    sep: str
    def __init__(
        self, k: str, t: Optional[KeyType] = ..., sep: Optional[str] = ..., dotted: bool = ..., original: Optional[str] = ...,
    ) -> None: ...
    @property
    def delimiter(self) -> str: ...
    def is_dotted(self) -> bool: ...
    def is_bare(self) -> bool: ...
    def as_string(self) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Key) -> bool: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class Item(object):
    """
    An item within a TOML document.
    """

    def __init__(self, trivia: Trivia) -> None: ...
    @property
    def trivia(self) -> Trivia: ...
    @property
    def discriminant(self) -> int: ...
    def as_string(self) -> str: ...
    # Helpers
    def comment(self, comment: str) -> Item: ...
    def indent(self, indent: int) -> Item: ...
    def is_boolean(self) -> bool: ...
    def is_table(self) -> bool: ...
    def is_inline_table(self) -> bool: ...
    def is_aot(self) -> bool: ...
    def _getstate(self, protocol: int = ...) -> Tuple[Trivia]: ...
    def __reduce__(self) -> Tuple[Type[Key], Tuple[Trivia]]: ...
    def __reduce_ex__(self, protocol: int) -> Tuple[Type[Key], Tuple[Trivia]]: ...

class Trivia:
    indent: str
    comment_ws: str
    comment: str
    trail: str
    def __init__(
        self,
        indent: Optional[str] = ...,
        comment_ws: Optional[str] = ...,
        comment: Optional[str] = ...,
        trail: Optional[str] = ...,
    ) -> None: ...

class Table(Item, dict):
    def __init__(
        self,
        value: Container,
        trivia: Trivia,
        is_aot_element: bool,
        is_super_table: bool = ...,
        name: Optional[str] = ...,
        display_name: Optional[str] = ...,
    ) -> None: ...
    @property
    def value(self) -> Container: ...
    @property
    def discriminant(self) -> int: ...
    def add(self, key: Union[Key, Item, str], item: Any = ...) -> Item: ...
    def append(self, key: Union[Key, str], _item: Any) -> Table: ...
    def raw_append(self, key: Union[Key, str], _item: Any) -> Table: ...
    def remove(self, key: Union[Key, str]) -> Table: ...
    def is_aot_element(self) -> bool: ...
    def is_super_table(self) -> bool: ...
    def as_string(self) -> str: ...
    # Helpers
    def indent(self, indent: int) -> Table: ...
    def keys(self) -> Generator[str, None, None]: ...
    def values(self) -> Generator[Item, None, None]: ...
    def items(self) -> Generator[Tuple[str, Item], None, None]: ...
    def update(self, other: Dict[Any, Any]) -> None: ...
    def get(self, key: Any, default: Optional[Any] = ...) -> Any: ...
    def __contains__(self, key: Union[Key, str]) -> bool: ...
    def __getitem__(self, key: Union[Key, str]) -> Item: ...
    def __setitem__(self, key: Union[Key, str], value: Any) -> None: ...
    def __delitem__(self, key: Union[Key, str]) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class StringType(Enum):
    # Single Line Basic
    SLB = '"'
    # Multi Line Basic
    MLB = '"""'
    # Single Line Literal
    SLL = "'"
    # Multi Line Literal
    MLL = "'''"
    @property
    def unit(self) -> str: ...
    def is_basic(self) -> bool: ...
    def is_literal(self) -> bool: ...
    def is_singleline(self) -> bool: ...
    def is_multiline(self) -> bool: ...
    def toggle(self) -> StringType: ...

class String(str, Item):
    """
    A string literal.
    """

    def __new__(cls, t: StringType, value: str, original: str, trivia: Trivia) -> None: ...
    def __init__(self, t: StringType, _: str, original: str, trivia: Trivia) -> None: ...
    @property
    def discriminant(self) -> int: ...
    @property
    def value(self) -> str: ...
    def as_string(self) -> str: ...
    def __add__(self, other: str) -> String: ...
    def __sub__(self, other: str) -> String: ...
    def _new(self, result: str) -> String: ...
