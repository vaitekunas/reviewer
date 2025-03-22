"""
User data model and repository

Is used to persistently store and represent a User.
For transportation purposes UserDTO is used.
"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Session
import bcrypt
from typing import Optional

from . import ORM_BASE
from ..interfaces import Repository
from ..dto import UserDTO


class User(ORM_BASE):
    __tablename__ = "user"

    id            = mapped_column(Integer, primary_key=True)
    username      = mapped_column(String,  nullable=False, unique=True)
    password_hash = mapped_column(String,  nullable=False)


class UserRepository(Repository):

    def _clean_username(self, username: str) -> str:
        return username.lower().strip()

    def _create_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode("utf-8")

    def add_user(self, 
                 session:  Session,
                 username: str,
                 password: str) -> Optional[UserDTO]:

        """
        Saves a user to the database if no such user exists
        """

        user_exists = (session
                        .query(User)
                        .filter(User.username == (username_c := self._clean_username(username)))
                        .first()) is not None

        if user_exists:
            return None

        password_hash = self._create_password_hash(password = password)
    
        user = User(username      = username_c,
                    password_hash = password_hash)

        session.add(user)
        session.flush()

        return UserDTO(user_id = user.id,
                       username = user.username)


    def get_user_by_id(self,
                       session: Session,
                       user_id: int) -> Optional[UserDTO]:
        """
        Retrieves a UserDTO based on the user ID
        """

        user = (session
                .query(User)
                .filter(User.id == user_id)
                .first())

        if user is None:
            return None

        return UserDTO(user_id       = user.id,
                       username      = user.username)

    def get_user_by_username(self,
                             session: Session,
                             username: str) -> Optional[UserDTO]:
        """
        Retrieves a UserDTO based on the username 
        """

        user = (session
                .query(User)
                .filter(User.username == (username_c := self._clean_username(username)))
                .first())

        if user is None:
            return None

        return UserDTO(user_id       = user.id,
                       username      = username_c)

    def is_valid_credentials(self,
                             session: Session,
                             username: str,
                             password: str) -> bool:
        """
        Validates provided credentials 
        """

        user = (session
                .query(User)
                .filter(User.username == self._clean_username(username))
                .first())

        if user is None:
            return False

        return bcrypt.checkpw(password.encode(), str(user.password_hash).encode())
