"""
Controllers for the analytics service.
"""

__all__ = ["get_method_types", 
           "get_methods", 
           "get_methods_of_type", 
           "get_method",

           "get_workflows",
           "get_workflow_by_name",
           "create_workflow",
           "modify_workflow",
           "delete_workflow",

           "get_analysis",
           "get_analysis_by_name",
           "create_analysis",
           "modify_analysis",
           "delete_analysis",
           "run_analysis"
           ]

import io
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Optional
from fastapi import File, HTTPException, Header, Response, UploadFile, status
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

@app.get("/api/method/type", tags=["analytics :: method"])
def get_method_types() -> list[str]:
    return [x.value for x in MethodType]


@app.get("/api/method", tags=["analytics :: method"])
def get_methods() -> dict[MethodType, dict[str, MethodDTO]]:
    
    result = {}
    for mtype, mregistrations in runtime.services.analytics.get_methods().items():
        if (mt := mtype.value) not in result:
            result[mt] = {}

        for m in mregistrations:
            result[mt][m.name] = MethodDTO(name        = m.name,
                                           description = m.description,
                                           module      = str(m.method_class.__module__),
                                           classname   = str(m.method_class.__name__),
                                           method_type = mtype,
                                           required    = {k: v.to_dict() for k, v in m.required_fields.items()},
                                           config      = m.method_config().to_dict())

    return result

@app.get("/api/method/{method_type}", tags=["analytics :: method"])
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
                           module      = str(m.method_class.__module__),
                           classname   = str(m.method_class.__name__).lower(),
                           method_type = mt[0],
                           required    = {k: v.to_dict() for k, v in m.required_fields.items()},
                           config      = m.method_config().to_dict())

        methods.append(method)

    return methods

@app.get("/api/method/{method_type}/{method_class}", tags=["analytics :: method"])
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
                       module      = str(m.method_class.__module__),
                       classname   = str(m.method_class.__name__).lower(),
                       method_type = mt[0],
                       required    = {k: v.to_dict() for k, v in m.required_fields.items()},
                       config      = m.method_config().to_dict())

    return method

##################################
# API: workflow
##################################

@app.get("/api/workflow", tags=["analytics :: workflow"])
def get_workflows(session_token: str = Header(...)) -> list[WorkflowDTO]:

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)
        workflows = analytics.get_workflows(t, user)

    return workflows

@app.get("/api/workflow/{workflow_name}", tags=["analytics :: workflow"])
def get_workflow_by_name(workflow_name: str,
                         session_token: str = Header(...)) -> Optional[WorkflowDTO]:

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)
        workflow = analytics.get_workflow_by_name(t, user, workflow_name)

    return workflow

@app.post("/api/workflow", tags=["analytics :: workflow"])
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

@app.put("/api/workflow/{workflow_name}", tags=["analytics :: workflow"])
def modify_workflow(workflow_name: str,
                    workflow:      WorkflowDTO,
                    session_token: str = Header(...)) -> None:
    """
    Modifies an existing workflow
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

@app.delete("/api/workflow/{workflow_name}", tags=["analytics :: workflow"])
def delete_workflow(workflow_name: str,
                    session_token: str = Header(...)) -> None:
    """
    Deletes an existing workflow
    """

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

##################################
# API: dataset
##################################

def _get_dataframe(contents: io.BytesIO) -> pd.DataFrame:

    df = pd.read_csv(contents, sep=";", decimal = ",", encoding="utf-8") 
    df.columns = [x.strip().lower().replace(" ","_") for x in df.columns]

    return df

@app.get("/api/dataset", tags=["analytics :: dataset"])
def get_datasets(session_token: str = Header(...)) -> list[DatasetDTO]:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)
        datasets = analytics.get_datasets(t, user)
        
    return datasets

@app.get("/api/dataset/{dataset_name}", tags=["analytics :: dataset"])
def get_dataset_by_name(dataset_name: str,
                        session_token: str = Header(...)) -> Optional[DatasetDTO]:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)
        dataset = analytics.get_dataset_by_name(t, user, dataset_name, with_data=False)
        
    return dataset

@app.post("/api/dataset/{dataset_name}", tags=["analytics :: dataset"])
def create_dataset(dataset_name: str,
                   dataset: UploadFile = File(...),
                   session_token: str = Header(...)) -> Optional[DatasetDTO]:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        try:
            contents = io.BytesIO(dataset.file.read())
            df = _get_dataframe(contents)

            dataset_dto = DatasetDTO(name      = dataset_name,
                                     n_rows    = df.shape[0],
                                     n_columns = df.shape[1],
                                     columns   = [str(x) for x in df.columns],
                                     data      = df.to_dict("list"))

            analytics.register_dataset(t, 
                                       user    = user, 
                                       name    = dataset_name,
                                       dataset = dataset_dto)
            t.commit()

            dataset_dto.data = None

            return dataset_dto

        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

        finally:
            dataset.file.close() 

@app.put("/api/dataset/{dataset_name}", tags=["analytics :: dataset"])
def modify_dataset(dataset_name: str,
                   dataset: UploadFile = File(...),
                   session_token: str = Header(...)) -> None:
    """
    Modifies an existing dataset
    """

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        # Save modification
        try:
            contents = io.BytesIO(dataset.file.read())
            df = _get_dataframe(contents)

            analytics.register_dataset(t, 
                                       user      = user, 
                                       name      = dataset_name,
                                       dataset   = DatasetDTO(name = dataset_name,
                                                            n_rows    = df.shape[0],
                                                            n_columns = df.shape[1],
                                                            columns   = [str(x) for x in df.columns],
                                                            data      = df.to_dict("list")),
                                       overwrite = True)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))
        finally:
            dataset.file.close() 

    return None

@app.delete("/api/dataset/{dataset_name}", tags=["analytics :: dataset"])
def delete_dataset(dataset_name: str,
                   session_token: str = Header(...)) -> None:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        try:
            analytics.unregister_dataset(t, user, dataset_name)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

##################################
# API: analysis
##################################

@app.get("/api/analysis", tags=["analytics :: analysis"])
def get_analysis(session_token: str = Header(...)) -> list[AnalysisDTO]:

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)
        analysis = analytics.get_analysis(t, user)

    return analysis

@app.get("/api/analysis/{analysis_name}", tags=["analytics :: analysis"])
def get_analysis_by_name(analysis_name: str,
                         session_token: str = Header(...)) -> Optional[AnalysisDTO]:
    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)
        analysis = analytics.get_analysis_by_name(t, user, analysis_name)

    return analysis

@app.post("/api/analysis/requirements", tags=["analytics :: analysis"])
def get_analysis_fields(analysis: AnalysisDTO) -> AnalysisFieldsDTO:
                        
    # Services
    analytics = runtime.services.analytics

    return analytics.get_analysis_fields(analysis)

@app.post("/api/analysis", tags=["analytics :: analysis"])
def create_analysis(analysis:      AnalysisDTO,
                    session_token: str = Header(...)) -> None:
    """
    Create a new analysis

    The analysis must have a unique name.
    """

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user     = _get_user(t, session_token)

        try:
            analytics.register_analysis(t, user, analysis)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

@app.put("/api/analysis/{analysis_name}", tags=["analytics :: analysis"])
def modify_analysis(analysis_name: str,
                    analysis:      AnalysisDTO,
                    session_token: str = Header(...)) -> None:
    """
    Modifies an existing analysis
    """

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user     = _get_user(t, session_token)

        try:
            analytics.register_analysis(t, user, analysis, analysis_name, overwrite = True)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

@app.delete("/api/analysis/{analysis_name}", tags=["analytics :: analysis"])
def delete_analysis(analysis_name: str,
                    session_token: str = Header(...)) -> None:
    """
    Deletes an existing analysis
    """

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user = _get_user(t, session_token)

        try:
            analytics.unregister_analysis(t, user, analysis_name)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

@app.post("/api/analysis/{analysis_name}", tags=["analytics :: analysis"])
def run_analysis(analysis_name: str,
                 run_setup:     RunSetupDTO,
                 session_token: str = Header(...)) -> None:
    """
    Runs an existing analysis

    """

    # Services
    analytics = runtime.services.analytics

    # Workflows
    with runtime.transaction as t:
        user = _get_user(t, session_token)

        try:
            analytics.run_analysis(t, 
                                   user          = user, 
                                   analysis_name = analysis_name,
                                   dataset_name  = run_setup.dataset_name, 
                                   mapping       = run_setup.mapping, 
                                   analysis      = run_setup.analysis)
            t.commit()
        except Exception as e:
            t.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = str(e))

    return None

##################################
# API: results
##################################

@app.get("/api/results/{run_id}", tags=["analytics :: results"])
def get_results(run_id: int,
                session_token: str = Header(...)) -> Optional[ResultsDTO]:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user    = _get_user(t, session_token)
        results = analytics.get_results(t, user, run_id)

    return results

@app.get("/api/results/{run_id}/{result_name}", tags=["analytics :: results"])
def get_result_by_name(run_id: int,
                       result_name: str,
                       session_token: str = Header(...)) -> Optional[ResultDTO]:
    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user   = _get_user(t, session_token)
        result = analytics.get_result_by_name(t, user, run_id, result_name)

    return result

@app.delete("/api/results/{run_id}", tags=["analytics :: results"])
def delete_results(run_id: int,
                   session_token: str = Header(...)) -> None:
    """
    Deletes all results of a run
    """

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        user   = _get_user(t, session_token)
        analytics.unregister_results(t, user, run_id)

    return None

##################################
# API: method
##################################

@app.get("/api/statistics", tags=["statistics"])
def get_statistics(session_token: str | None = Header(None)) -> StatisticsDTO:

    # Services
    analytics = runtime.services.analytics

    with runtime.transaction as t:
        if session_token:
            user   = _get_user(t, session_token)
        else:
            user = None

        return analytics.get_statistics(t, user)
