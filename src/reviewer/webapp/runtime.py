"""
Global representation of the current runtime. 
"""

__all__ = ["Runtime"]

import os
import logging
from logging import Logger
from collections.abc import Generator
from dataclasses import dataclass
from contextlib import contextmanager
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.session import sessionmaker, Session
from sqlalchemy.engine import Engine

from .interfaces import ApplicationService, AnalyticsService,\
                        ExternalService 

class Runtime:
    """
    Used to register the data persistence layer, services and some configuration.

    An instance of runtime is available globally to all the controllers, in order
    to have access to available services and active configuration.
    """

    @dataclass
    class Services:
        """
        Representation of known services used in this application.
        """
        application: ApplicationService
        analytics:   AnalyticsService
        external:    ExternalService

    def __init__(self, 
                 ORM_BASE:    DeclarativeBase,
                 WORK_DIR:    str  = os.getcwd(),
                 session_ttl: int  = 3600) -> None:

        self._ob          = ORM_BASE
        self._sm          = None
        self._services    = None
        self._workdir     = WORK_DIR
        self._session_ttl = session_ttl
        self._llm_host    = "localhost:11434"

        self._logger_parent = logging.getLogger()
        self._logger = self._logger_parent.getChild("runtime")

    def register_database(self, engine: Engine) -> None:
        """
        Registers a persistence layer.

        Parameters:
            engine (Engine): sqlalchemy engine

        Returns:
            None
        """

        self._sm = sessionmaker(bind = engine)

        self._ob.metadata.create_all(engine)
        for table in list(self._ob.metadata.tables.keys()):
            self.log(f"Table '{table}' created")

        self.log("database registered")

    def register_services(self, 
                          application: ApplicationService,
                          analytics:   AnalyticsService,
                          external:    ExternalService):
                          
        """
        Registers services at runtime. These services are then available to all 
        the controllers in the application.

        Parameters:
            application (ApplicationService):   application service (handles user sessions)
            analytics   (AnalyticsService):     pipeline service (handles analytics)
            storage     (DocumentStoreService): storage service (handles persistence)
            external    (ExternalService):      external service (handles LLMs)
        """
                          
        self._services = Runtime.Services(application,
                                          analytics,
                                          external)

        self.log("services registered")

    def log(self, msg: str) -> None:
        """
        Centralized method for logging.
        """
        self._logger.info(msg)

    @property
    @contextmanager 
    def transaction(self) -> Generator[Session, None, None]:
        """
        A context manager for initializing a database transaction.

        Parameters:
            None

        Returns:
            Session: database transaction in form of a Generator
        """
        if self._sm is None:
            raise Exception("Runtime has no registered session maker")

        yield self._sm()

    @property
    def services(self) -> 'Runtime.Services':
        """
        A convenience property used to access registered services.

        Parameters:
            None

        Returns:
            Services: data class with all the registered services
        """
        if self._services is None:
            raise Exception("Runtime has no registered services")

        return self._services

    @property
    def logger(self) -> Logger:
        """
        Returns a centralized Logger instance for further forking.
        """
        return self._logger_parent

    @property
    def workdir(self) -> str:
        """
        Returns the configured work directory
        """
        return self._workdir

    @workdir.setter
    def workdir(self, value: str) -> None:
        """
        Sets / overwrites the value of the work directory
        """
        self._workdir = value

    @property
    def session_ttl(self) -> int:
        """
        Returns the time-to-live value for user sessions.
        """
        return self._session_ttl

    @session_ttl.setter
    def session_ttl(self, value: int) -> None:
        """
        Sets the value for user session TTL.
        """
        self._session_ttl = value

    @property
    def llm_host(self) -> str:
        """
        Returns LLM host
        """
        return self._llm_host

    @llm_host.setter
    def llm_host(self, value: str) -> None:
        """
        Sets LLM host
        """
        self._llm_host = value

