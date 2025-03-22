"""
User Session data model and repository

Is used to persistently store and represent a user Session
For transportation purposes SessionTokenDTO is used.
"""
import secrets
from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Session, mapped_column

from . import ORM_BASE
from .user import User

from ..interfaces import Repository
from ..dto import SessionTokenDTO


class UserSession(ORM_BASE):
    __tablename__ = "session"

    id            = mapped_column(Integer, primary_key=True)
    user_id       = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    token         = mapped_column(String,  nullable=False)
    ttl_timestamp = mapped_column(Integer,  nullable=False)


class UserSessionRepository(Repository):
    

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(nbytes = 64).lower()[:64]


    @property
    def timestamp(self) -> int:
        return int(datetime.now().timestamp())

        
    def create_session(self,
                     session:     Session,
                     user_id:     int,
                     session_ttl: int) -> SessionTokenDTO:

        m = UserSession(user_id       = user_id,
                        token         = self._generate_token(),
                        ttl_timestamp = self.timestamp + session_ttl)

        session.add(m)

        user = (session 
                    .query(User)
                    .filter(User.id == user_id)
                    .first())

        if user is None:
            raise Exception(f"Unknown user '{user_id}'")

        return SessionTokenDTO(user_id    = user_id, 
                               username   = user.username,
                               token      = m.token, 
                               expires_at = m.ttl_timestamp)

    def invalidate_session(self, 
                           session: Session,
                           token: SessionTokenDTO) -> None:

        exists = (session
                    .query(UserSession)
                    .filter(UserSession.user_id == token.user_id,
                            UserSession.token   == token.token)
                    .first())

        if exists:
            session.delete(exists)


    def cleanup_sessions(self, 
                         session: Session) -> None:

        expired = (session
                    .query(UserSession)
                    .filter(UserSession.ttl_timestamp < self.timestamp)
                    .all())

        for us in expired:
            session.delete(us)

        session.flush()

    def get_session(self,
                    session: Session,
                    token_str: str) -> Optional[SessionTokenDTO]:

        exists = (session
                    .query(UserSession)
                    .join(User, User.id == UserSession.user_id)
                    .filter(UserSession.token == token_str,
                            UserSession.ttl_timestamp >= self.timestamp)
                    .with_entities(User.id, User.username, 
                                   UserSession.token, UserSession.ttl_timestamp)
                    .first())

        if not exists:
            return None

        return SessionTokenDTO(user_id    = exists[0],
                               username   = exists[1],
                               token      = exists[2],
                               expires_at = exists[3])

