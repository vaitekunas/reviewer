__all__ = ["Figure"]

from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.figure import Figure as PltFigure
from typing import Any, override

from .interface import IFigure


class Figure(IFigure):

    def __init__(self, fig: PltFigure) -> None:
        super().__init__()

        self._fig = fig

    @override
    def to_bytes(self) -> bytes:
        with BytesIO() as buffer:
            self._fig.savefig(buffer, format="png")
            buffer.seek(0)
            content = buffer.read()

        return content

    @property
    @override
    def raw(self) -> Any:
        return self._fig

    @staticmethod
    def new(fig: Any) -> 'Figure':
        return Figure(fig)
