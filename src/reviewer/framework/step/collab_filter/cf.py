__all__ = ["CollaborativeFilteringConfig", "CollaborativeFiltering"]

from pandas import DataFrame
from surprise import SVD, Reader
from surprise.model_selection import GridSearchCV
from surprise import Dataset as SDataset
from dataclasses import asdict, dataclass
from typing import Any, override

from ...interface import IConfig, IDataset, IPredictor
from ...aliases import AnalysisField, FieldSchema


@dataclass
class CollaborativeFilteringConfig(IConfig):

    user_field:    str = "user_id"
    product_field: str = "product_id"
    rating_field:  str = "rating"

    min_rating: int = 1
    max_rating: int = 5

    output_field_prefix: str = "recommendation"
    max_recommendations: int = 5

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class CollaborativeFiltering(IPredictor[CollaborativeFilteringConfig]):

    def __init__(self, config: CollaborativeFilteringConfig | None = None) -> None:
        super().__init__(config)

        self._name = "Collaborative filtering"
        self._config = config or self.get_default_config()
        self._model = SVD()
        self._is_trained = False

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> CollaborativeFilteringConfig:
        return CollaborativeFilteringConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.rating_field: FieldSchema(dtype = int,
                                                       description = "Numerical rating of the review"),

                self._config.product_field: FieldSchema(dtype = int,
                                                        description = "Product or service ID"),

                self._config.user_field: FieldSchema(dtype = int,
                                                     description = "User ID")}

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.output_field_prefix: FieldSchema(dtype = int,
                                                              prefix = True,
                                                              description = "Recommended product or service ID")}

    # Predictor
    def _get_usermatrix(self, data: IDataset) -> DataFrame:

        users    = data.get_field_values(self._config.user_field)
        products = data.get_field_values(self._config.product_field)
        ratings  = data.get_field_values(self._config.rating_field)

        df = DataFrame({"user":   users,
                        "item":   products,
                        "rating": ratings})

        return df

    @property
    @override
    def is_trained(self) -> bool:
        return self._is_trained

    @override
    def train(self, data: IDataset) -> None:

        df = self._get_usermatrix(data)

        reader = Reader(rating_scale=(self._config.min_rating, 
                                      self._config.max_rating))

        ds = SDataset.load_from_df(df, reader)
        trainset = ds.build_full_trainset()
        self._model.fit(trainset)

        self._is_trained = True

    @override
    def predict(self, data: IDataset) -> IDataset:
        assert self._is_trained, "Model has not been trained"

        data = data.copy()

        users = data.get_field_values(self._config.user_field)

        df = self._get_usermatrix(data)

        # Unique users and products
        uusers    = df["user"].drop_duplicates().to_list()
        uproducts = set(df["item"].drop_duplicates().to_list())

        # Predict recommendations
        user_recommendations = {}
        mr = self._config.max_recommendations
        for user in uusers:
            candidates  = sorted(list(uproducts - set(df.query(f"user == {user}")["item"])))
            predictions = [self._model.predict(user, p) for p in candidates]
            top_items   = (sorted(predictions, key=lambda x: x.est, reverse=True) + [None] * mr)[:mr]

            user_recommendations[user] = [int(x.iid) if x is not None else 0 for x in top_items]

        # Map recommendations
        for i in range(self._config.max_recommendations):
            rname   = self._config.output_field_prefix + str(i+1)
            rvalues = [user_recommendations[u][i] for u in users]

            data.set_field_values(rname, rvalues)

        return data
