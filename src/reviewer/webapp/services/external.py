__all__ = ["DefaultExternalService"]


import logging
from logging import Logger

from ..interfaces import ExternalService


class DefaultExternalService(ExternalService):

    def __init__(self, 
                 llm_host: str,
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("external")
        else:
            self._logger = logging.getLogger("external")

        self._llm_host = llm_host
        self._logger.info("ExternalService ready")

