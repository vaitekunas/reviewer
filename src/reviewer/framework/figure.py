from dataclasses import dataclass
import matplotlib.pyplot as plt
from typing import Any

@dataclass 
class Figure:
    raw_data: Any
    title:    str
    figure:   plt.Figure

