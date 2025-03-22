"""
Model repository interface
"""
from abc import ABC


class Repository(ABC):
    """
    Abstract class representing a model repository

    This class is used purely for typing and has no methods.
    """

    def __init__(self) -> None:
        super().__init__()



