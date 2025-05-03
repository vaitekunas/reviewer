__all__ = ["IConfig"]

import re
from abc import ABC, abstractmethod
from typing import Any


class IConfig(ABC):

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError("abstract method")

    def _cast(self, old_value: Any, new_value: Any) -> Any:

        # Split to parts
        if not (isinstance(new_value, list) or isinstance(new_value, tuple)):
            raw_values = re.sub("[()[]]","",str(new_value)).split(",")
        else:
            raw_values = new_value

        # Cast
        if isinstance(old_value, tuple):
            if len(old_value):
                transformed_value = tuple([self._cast(old_value[0], x) for x in raw_values])
            else:
                transformed_value = raw_values

        elif isinstance(old_value, list):
            if len(old_value):
                transformed_value = [self._cast(old_value[0], x) for x in raw_values]
            else:
                transformed_value = raw_values

        elif isinstance(old_value, str):
            transformed_value = str(new_value)

        elif isinstance(old_value, bool):
            transformed_value = bool(new_value)

        elif isinstance(old_value, int):
            transformed_value = int(str(new_value))

        elif isinstance(old_value, float):
            transformed_value = float(str(new_value))

        else:
            transformed_value = old_value


        return transformed_value

    def update(self, values: dict[str, Any]) -> None:
        for k, v in values.items():
            if hasattr(self, k):
                old_value = getattr(self, k)
                try:
                    setattr(self, k, self._cast(old_value, v))
                except:
                    raise Exception(f"Invalid value format for '{k}'")
