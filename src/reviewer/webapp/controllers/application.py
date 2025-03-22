"""
Controllers for the application service.
"""
from typing import Optional
from fastapi import HTTPException, Header, status

from .. import app, runtime
from ..dto  import SessionTokenDTO, UserDTO

logger = runtime.logger.getChild("API/application")


@app.post("/api/user", tags=["application"])
def register(username: str, password: str) -> Optional[UserDTO]:
    """
    Registers a new user.

    Parameters:
        username (str): user name 
        password (str): user password 

    Returns:
        Optional[UserDTO]: user representation if registration successful
    """

    if len(username.strip()) < 3 or len(password.strip()) < 3:
            logger.warning("Invalid credentials (too short)")
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = "Credentials too short")

    with runtime.transaction as t:

        user = runtime.services.application.create_user(session  = t,
                                                        username = username,
                                                        password = password)

        if user is None:
            t.rollback()
            logger.warning("User not created")
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = "User not created")
            
        t.commit()
        logger.info(f"User '{username}' created")

        return user


@app.post("/api/session", tags=["application"])
def login(username: str, password: str) -> Optional[SessionTokenDTO]:
    """
    Creates a user session.

    Parameters:
        username (str): user name 
        password (str): user password 

    Returns:
        Optional[SessionTokenDTO]: user session in case of successful login.
    """

    application = runtime.services.application

    # Cleanup sessions
    with runtime.transaction as t:
        application.cleanup_sessions(session = t)
        t.commit()
        
    # Login
    with runtime.transaction as t:
        
        token = application.login(session     = t,
                                  username    = username,
                                  password    = password,
                                  session_ttl = runtime.session_ttl)

        if token is None:
            t.rollback()
            logger.warning("Invalid credentials")
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                detail = "Invalid credentials")
            
        t.commit()

        logger.warning(f"User '{token.user_id}' logged in")

        return token


@app.delete("/api/session", tags=["application"])
def logout(session_token: str = Header(...)) -> None:
    """
    Deletes an existing user session.

    Parameters:
        session_token (str): session token

    Returns:
        None
    """

    application = runtime.services.application

    # Cleanup sessions
    with runtime.transaction as t:
        application.cleanup_sessions(session = t)
        t.commit()

    # Logout
    with runtime.transaction as t:

        token = application.get_session_from_auth_str(session = t,
                                                      token_str = session_token)
        if token is None:
            logger.warning("Invalid token")
            t.rollback()
            return None

        application.logout(session = t,
                           token   = token)

        t.commit()

        logger.warning(f"User '{token.user_id}' logged out")


@app.put("/api/session", tags=["application"])
def renew_token(session_token: str = Header(...)) -> Optional[SessionTokenDTO]:
    """
    Renews an existing valid user session.

    Parameters:
        session_token (str): session token 

    Returns:
        Optional[SessionTokenDTO]: a new user session in case of successful renewal.
    """

    application = runtime.services.application

    # Cleanup sessions
    with runtime.transaction as t:
        application.cleanup_sessions(session = t)
        t.commit()

    # Renew token
    with runtime.transaction as t:

        token = application.get_session_from_auth_str(session = t, 
                                                      token_str = session_token)
        if not token:
            t.rollback()
            logger.warning("Invalid token")
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                detail = "Invalid token")

        new_token = application.renew_token(session     = t, 
                                            token       = token,
                                            session_ttl = runtime.session_ttl)
        if not new_token:
            t.rollback()
            logger.warning("Renewal failed")
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                detail = "Renewal failed")

        t.commit()

        return new_token

