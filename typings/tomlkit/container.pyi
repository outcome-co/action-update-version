from __future__ import annotations

from typing import Any, Dict, KeysView, Union

from tomlkit.items import Item, Key

class Container(Dict[Union[Key, str], Any]):  # noqa: WPS600
    def __getitem__(self, key: Union[Key, str]) -> Union[Item, Container]: ...
    def __setitem__(self, key: Union[Key, str], value: Any) -> None: ...
    def keys(self) -> KeysView[str]: ...
    def as_string(self) -> str: ...
