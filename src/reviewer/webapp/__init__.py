import logging
from fastapi import FastAPI

from .models import *
from .runtime import Runtime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)-12s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(
    title="Customer review analytics",
    description="""
    Prototype software for analysing and visualizing customer reviews using
    simple data science techniques.

    This software is represents the practical implementation phase of a 
    bachelor thesis at FernUniversität in Hagen.
    """,
    version="0.9.0rc",
    contact={
        "name": "Mindaugas Vaitekunas",
        "url": "https://linkedin.com/in/vaitekunas",
    },
    license_info={
        "name": "Licence: GPLv3",
        "url": "https://choosealicense.com/licenses/gpl-3.0/",
    },
        )

runtime = Runtime(ORM_BASE)
