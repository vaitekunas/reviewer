import os
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool

from . import app, runtime

from .services    import *
from .controllers import *
from .utilities   import prepare_workdir

from ..framework import step

# Application parameters
WORK_DIR    = os.path.expanduser(os.environ.get("WORK_DIR", "~/reviewer"))
DB_NAME     = os.environ.get("DB_NAME", "reviews.sqlite")
SESSION_TTL = os.environ.get("SESSION_TTL", 60*60*24)
LLM_HOST    = os.environ.get("OLLAMA_HOST", "localhost:11434")

# Active configuration
print("#"*100)
runtime.log(f"Starting Customer Review Analytics")
runtime.log(f"WORK_DIR: '{WORK_DIR}'")
runtime.log(f"DB_NAME:  '{DB_NAME}'")
runtime.log(f"LLM_HOST: '{LLM_HOST}'")
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

# Register methods
analytics_service = DefaultAnalyticsService(logger = runtime.logger)

(analytics_service
    # Preprocessing
    .register_method(MethodType.PREPROCESSOR, step.Preprocessor)

    # Embedding
    .register_method(MethodType.EMBEDDER, step.TfIdfEmbedder)
 
    # Descriptive statistics
    .register_method(MethodType.DESCRIPTIVE_STATISTIC, step.NgramAnalyser)
    .register_method(MethodType.DESCRIPTIVE_STATISTIC, step.RatingAnalyser)

    # Temporal descriptive statistics
    .register_method(MethodType.TEMPORAL_STATISTIC, step.TemporalNgramAnalyser)
    .register_method(MethodType.TEMPORAL_STATISTIC, step.TemporalRatingAnalyser)

    # Classifiers
    .register_method(MethodType.CLASSIFIER, step.LogisticRegression)
    .register_method(MethodType.CLASSIFIER, step.SVM)
    .register_method(MethodType.CLASSIFIER, step.DecisionTree)
    .register_method(MethodType.CLASSIFIER, step.RandomForest)
    .register_method(MethodType.CLASSIFIER, step.NaiveBayes)

    # Recommenders
    .register_method(MethodType.RECOMMENDER, step.CollaborativeFiltering)

    # Evaluators
    .register_method(MethodType.EVALUATION_METRIC, step.BinaryEvaluationMetric)
    .register_method(MethodType.EVALUATION_METRIC, step.ROC)
    .register_method(MethodType.EVALUATION_METRIC, step.ConfusionMatrix)

    # Visualizers
    .register_method(MethodType.VISUALIZATION, step.WordCloud)
    .register_method(MethodType.VISUALIZATION, step.TSneVisualization)
    .register_method(MethodType.VISUALIZATION, step.ScatterPlot)
    .register_method(MethodType.VISUALIZATION, step.LinePlot)
    .register_method(MethodType.VISUALIZATION, step.BarChart)
 )

# Register database and services 
runtime.register_database(engine = engine)

runtime.register_services(analytics   = analytics_service,
                          application = DefaultApplicationService(logger = runtime.logger), 
                          external    = DefaultExternalService(logger  = runtime.logger, llm_host = runtime.llm_host))
                                                               
# Construct application
runtime.log("App ready")
