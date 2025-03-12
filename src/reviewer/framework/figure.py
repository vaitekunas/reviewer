__all__ = ["Figure"]

from dataclasses import dataclass
from matplotlib import figure
from typing import Any

from .interface import IFigure

@dataclass 
class Figure(IFigure):
    raw_data: Any
    title:    str
    figure:   figure.Figure

