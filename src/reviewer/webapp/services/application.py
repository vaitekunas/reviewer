"""
Default Application Subsystem.

Implements app.interfaces.service.ApplicationService.
For documentation, see there.
"""

__all__ = ["DefaultApplicationService"]

import logging
from logging import Logger
from typing import Optional
from sqlalchemy.orm import Session

from ..interfaces import ApplicationService
from ..models.user import UserRepository
from ..models.session import UserSessionRepository
from ..dto import SessionTokenDTO, UserDTO


class DefaultApplicationService(ApplicationService):

    def __init__(self, 
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("application")
        else:
            self._logger = logging.getLogger("application")

        self._u_repo  = UserRepository()
        self._us_repo = UserSessionRepository()

        self._logger.info("ApplicationService ready")

    def create_user(self, 
                    session:  Session,
                    username: str, 
                    password: str) -> Optional[UserDTO]:

        if not len(username.strip()) or not len(password.strip()):
            return None

        return self._u_repo.add_user(session  = session, 
                                     username = username,
                                     password = password)

    def login(self, 
              session:     Session,
              username:    str, 
              password:    str,
              session_ttl: int) -> Optional[SessionTokenDTO]:

        # Validate credentials
        if not self._u_repo.is_valid_credentials(session = session,
                                                 username = username,
                                                 password = password):

            return None

        # Retrieve user
        user = self._u_repo.get_user_by_username(session  = session,
                                                 username = username)

        if user is None:
            return None

        # Create session token
        token = self._us_repo.create_session(session     = session,
                                             user_id     = user.user_id,
                                             session_ttl = session_ttl)

        return token


    def logout(self, 
               session: Session, 
               token: SessionTokenDTO) -> None:

        self._us_repo.invalidate_session(session = session,
                                         token = token)


    def get_user_from_auth_str(self,
                               session:   Session,
                               token_str: Optional[str]) -> Optional[UserDTO]:

        if token_str is None:
            return None

        token = self._us_repo.get_session(session = session,
                                          token_str = token_str)

        if not token:
            return None

        return self._u_repo.get_user_by_id(session = session, user_id = token.user_id)

    def get_session_from_auth_str(self, 
                                  session: Session, 
                                  token_str: Optional[str]) -> Optional[SessionTokenDTO]:

        if token_str is None:
            return None

        return self._us_repo.get_session(session   = session,
                                         token_str = token_str)


    def cleanup_sessions(self, session: Session) -> None:
        self._us_repo.cleanup_sessions(session = session)


    def renew_token(self, 
                    session:     Session, 
                    token:       SessionTokenDTO,
                    session_ttl: int) -> Optional[SessionTokenDTO]:

        # Validate session
        if not self._us_repo.get_session(session = session, token_str = token.token):
            return None 

        # Create new session
        new_token = self._us_repo.create_session(session     = session, 
                                                 user_id     = token.user_id,
                                                 session_ttl = session_ttl)

        # Invalidate old session
        self._us_repo.invalidate_session(session = session, token = token)

        return new_token

