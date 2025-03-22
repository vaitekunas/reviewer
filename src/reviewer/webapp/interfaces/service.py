"""
Service / Subsystem interfaces
"""
__all__ = ["ApplicationService",
           "AnalyticsService",
           "ExternalService"]
           

from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from sqlalchemy.orm import Session
from ..dto import *


class Service(ABC):
    """
    Abstract Service class.
    """

    def __init__(self) -> None:
        super().__init__()


class ApplicationService(Service):
    """
    Application Service / Subsystem 
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create_user(self, 
                    session: Session,
                    username: str, 
                    password: str) -> Optional[UserDTO]:
        """
        Creates a new user.

        Parameters:
            session (Session): database transaction
            username (str): user name 
            password (str): user password

        Returns:
            Optional[UserDTO]: user representation in case of successful registration.
        """
        raise NotImplementedError()

    @abstractmethod
    def login(self, 
              session:     Session,
              username:    str, 
              password:    str,
              session_ttl: int) -> Optional[SessionTokenDTO]:
        """
        Creates user session.

        Parameters:
            session (Session): database transaction 
            username (str): user name.
            password (str): user password.
            session_ttl (int): duration of the session.
        
        Returns:
            Optional[SessionTokenDTO]: user session in case of successful login

        """
        raise NotImplementedError()

    @abstractmethod
    def logout(self, 
               session: Session,
               token:   SessionTokenDTO) -> None:
        """
        Deletes an existing user session.

        Parameters:
            session (Session): database transaction 
            token (SessionTokenDTO): user session

        Returns:
            None
        """
        raise NotImplementedError()

    @abstractmethod
    def renew_token(self, 
                    session:     Session, 
                    token:       SessionTokenDTO,
                    session_ttl: int) -> Optional[SessionTokenDTO]:
        """
        Renews a valid user session.

        Parameters:
            session (Session): database transaction 
            token (SessionTokenDTO): user session
            session_ttl (int): duration of the session.

        Returns:
            Optional[SessionTokenDTO]: user session in case of successful renewal
        """
        raise NotImplementedError()
        
    @abstractmethod
    def cleanup_sessions(self, session: Session) -> None:
        """
        Deletes stale user sessions.

        Parameters:
            session (Session): database transaction 

        Returns: 
            None
        """
        raise NotImplementedError()

    @abstractmethod
    def get_user_from_auth_str(self, 
                               session: Session, 
                               token_str: Optional[str]) -> Optional[UserDTO]:
        """
        Returns user representation from a given session token.

        Parameters:
            session (Session): database transaction 
            token_str (str): session token 

        Returns:
            Optional[UserDTO]: user representation if session token is valid
        """

        raise NotImplementedError()

    @abstractmethod
    def get_session_from_auth_str(self, 
                                  session: Session, 
                                  token_str: Optional[str]) -> Optional[SessionTokenDTO]:
        """
        Returns user session given a session token.

        Parameters:
            session (Session): database transaction 
            token_str (str): session token 

        Returns:
            Optional[SessionTokenDTO]: user session if session token is valid
        """

        raise NotImplementedError()


class AnalyticsService(Service):

    @abstractmethod
    def register_method(self, method_type: MethodType, method_class: Type[Any]) -> 'AnalyticsService':
        ...

    @abstractmethod
    def get_registered_methods(self) -> dict[MethodType, dict[str, Type[Any]]]:
        ...
    
    @abstractmethod
    def define_workflow(self, 
                        name: str,
                        description: str, 
                        methods: list[MethodDTO]) -> WorkflowDTO:
        ...

    @abstractmethod
    def define_analysis(self, 
                        name: str,
                        description: str,
                        workflows: list[WorkflowDTO]) -> AnalysisDTO:
        ...

    @abstractmethod
    def run_analysis(self, analysis: AnalysisDTO) -> ResultsDTO:
        ...


class ExternalService(Service):
    """
    Pipeline Service / Subsystem 

    Implements methods required to extract a list of Named-Entity Co-Occurrences
    from a list of articles
    """

    def __init__(self) -> None:
        super().__init__()

