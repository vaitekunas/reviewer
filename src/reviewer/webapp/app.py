import os
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool

from . import app, runtime

from .services    import *
from .controllers import *
from .utilities   import prepare_workdir

from ..framework import step

# Application parameters
WORK_DIR        = os.path.expanduser(os.environ.get("WORK_DIR", "~/reviewer"))
METHOD_REGISTRY = os.environ.get("METHOD_REGISTRY", "method_registry.json")
DB_NAME         = os.environ.get("DB_NAME", "reviews.sqlite")
SESSION_TTL     = os.environ.get("SESSION_TTL", 60*60*24)
LLM_HOST        = os.environ.get("LLM_HOST", "localhost:11434")

# Active configuration
print("#"*100)
runtime.log(f"Starting Customer Review Analytics")
runtime.log(f"WORK_DIR:        '{WORK_DIR}'")
runtime.log(f"METHOD_REGISTRY: '{METHOD_REGISTRY}'")
runtime.log(f"DB_NAME:         '{DB_NAME}'")
runtime.log(f"LLM_HOST:        '{LLM_HOST}'")
print("#"*100)

# Prepare work dir
prepare_workdir(root = WORK_DIR)

# Initialize database
if not DB_NAME:
    engine = create_engine("sqlite:///", poolclass=SingletonThreadPool)
else:
    engine = create_engine(f"sqlite:///{WORK_DIR}/{DB_NAME}", poolclass=SingletonThreadPool)

# Configure runtime
runtime.workdir     = str(WORK_DIR)
runtime.session_ttl = int(SESSION_TTL)
runtime.llm_host    = str(LLM_HOST)

# Register database and services 
runtime.register_database(engine = engine)

runtime.register_services(application = DefaultApplicationService(logger = runtime.logger), 

                          analytics   = DefaultAnalyticsService(logger          = runtime.logger, 
                                                                work_dir        = WORK_DIR,
                                                                method_registry = METHOD_REGISTRY),

                          external    = DefaultExternalService(logger  = runtime.logger, llm_host = runtime.llm_host))
                                                               
# Construct application
runtime.log("App ready")
