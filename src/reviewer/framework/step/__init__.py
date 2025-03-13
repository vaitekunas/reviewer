import os
import nltk

os.environ["NLTK_CORPORA_PATH"] = os.path.expanduser(os.environ.get("NLTK_CORPORA_PATH", "~/nltk_data"))

nltk.data.path.append(os.environ["NLTK_CORPORA_PATH"])

try:
    from nltk.corpus import stopwords as stopwords
    _ = stopwords.words("english")
except:
    nltk.download("stopwords", download_dir = os.getenv("NLTK_CORPORA_PATH"))
    nltk.download("wordnet",   download_dir = os.getenv("NLTK_CORPORA_PATH"))
    nltk.download("punkt_tab", download_dir = os.getenv("NLTK_CORPORA_PATH"))

from .preprocessor import *
