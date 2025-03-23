"""
Controllers for the analytics service.
"""

__all__ = ["method_types", "methods", "methods_of_type", "method"]

from typing import Optional
from fastapi import HTTPException, Header, status

from .. import app, runtime
from ..dto  import *

logger = runtime.logger.getChild("API/analytics")

@app.get("/api/method/type", tags=["analytics"])
def method_types() -> list[str]:
    return [x.value for x in MethodType]


@app.get("/api/method", tags=["analytics"])
def methods() -> dict[MethodType, dict[str, MethodDTO]]:
    
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
def methods_of_type(method_type: str) -> list[MethodDTO]:
    
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
def method(method_type: str, method_class: str) -> Optional[MethodDTO]:
    
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
