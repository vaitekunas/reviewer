"""
Controllers for the analytics service.
"""

__all__ = ["get_method_types", 
           "get_methods", 
           "get_methods_of_type", 
           "get_method",

           "get_workflows",
           "create_workflow",
           "modify_workflow",
           "delete_workflow",
           ]

from typing import Any, Optional
from fastapi import HTTPException, Header, status
from sqlalchemy.orm.session import Session

from .. import app, runtime
from ..dto  import *

logger = runtime.logger.getChild("API/analytics")

# Supporting functions

def _get_user(t: Session, session_token: str) -> UserDTO:

    application = runtime.services.application

    # Get user
    user = application.get_user_from_auth_str(session   = t, 
                                              token_str = session_token)

    if user is None:
        logger.warning("Invalid user session")
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Invalid user session")

    return user

##################################
# API: method
##################################

@app.get("/api/method/type", tags=["analytics"])
def get_method_types() -> list[str]:
    return [x.value for x in MethodType]


@app.get("/api/method", tags=["analytics"])
def get_methods() -> dict[MethodType, dict[str, MethodDTO]]:
    
    result = {}
    for mtype, mregistrations in runtime.services.analytics.get_methods().items():
        if (mt := mtype.value) not in result:
            result[mt] = {}

        for m in mregistrations:
            result[mt][m.name] = MethodDTO(name        = m.name,
                                           description = m.description,
                                           classname   = str(m.method_class.__name__).lower(),
                                           config      = m.method_config().to_dict())

    return result

@app.get("/api/method/{method_type}", tags=["analytics"])
def get_methods_of_type(method_type: str) -> list[MethodDTO]:
    
    # Get MethodType
    mt = [x for x in MethodType if method_type.strip().lower() == x.value.strip().lower()]
    if not len(mt):
        return []

    # Return method 
    methods = []
    for m in runtime.services.analytics.get_methods().get(mt[0], []):
        method = MethodDTO(name        = m.name,
                           description = m.description,
                           classname   = str(m.method_class.__name__).lower(),
                           config      = m.method_config().to_dict())

        methods.append(method)

    return methods

@app.get("/api/method/{method_type}/{method_class}", tags=["analytics"])
def get_method(method_type: str, method_class: str) -> Optional[MethodDTO]:
    
    # Get MethodType
    mt = [x for x in MethodType if method_type.strip().lower() == x.value.strip().lower()]
    if not len(mt):
        return None

    # Get method registration
    methods = [x for x in runtime.services.analytics.get_methods()[mt[0]] 
                 if str(x.method_class.__name__).lower() == method_class.strip().lower()]

    if not len(methods):
        return None 

    # Return method 
    m = methods[0]
    method = MethodDTO(name        = m.name,
                       description = m.description,
                       classname   = str(m.method_class.__name__).lower(),
                       config      = m.method_config().to_dict())

    return method

##################################
# API: workflow
##################################

@app.get("/api/workflow", tags=["analytics"])
def get_workflows(session_token: str = Header(...)) -> list[WorkflowDTO]:

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)
        workflows = analytics.get_workflows(t, user)

    return workflows

@app.get("/api/workflow/{workflow_name}", tags=["analytics"])
def get_workflow(workflow_name: str,
                 session_token: str = Header(...)) -> Optional[WorkflowDTO]:

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)
        workflow = analytics.get_workflow(t, user, workflow_name)

    return workflow

@app.post("/api/workflow", tags=["analytics"])
def create_workflow(workflow:      WorkflowDTO,
                    session_token: str = Header(...)) -> None:
    """
    Create a new workflow.

    The workflow must have a unique name.
    """

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        try:
            analytics.register_workflow(t, user, workflow)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

@app.put("/api/workflow/{workflow_name}", tags=["analytics"])
def modify_workflow(workflow_name: str,
                    workflow:      WorkflowDTO,
                    session_token: str = Header(...)) -> None:
    """
    Create a new workflow.

    The workflow must have a unique name.
    """

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        # Save modification
        try:
            analytics.register_workflow(t, user, workflow, name = workflow_name, overwrite = True)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

@app.delete("/api/workflow/{workflow_name}", tags=["analytics"])
def delete_workflow(workflow_name: str,
                    session_token: str = Header(...)) -> None:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        try:
            analytics.unregister_workflow(t, user, workflow_name)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None



