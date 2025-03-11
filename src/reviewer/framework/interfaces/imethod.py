from abc import abstractmethod

from .iconfig import Configurable
from .iidentifiable import Identifiable


class Method(Identifiable, Configurable):
    ...    
