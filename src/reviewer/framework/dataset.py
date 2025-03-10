
class Dataset:

    @property
    def train_data(self) -> 'Dataset':
        ...

    @property
    def test_data(self) -> 'Dataset':
        ...

    @staticmethod
    def from_csv(path: str) -> 'Dataset':
        ...



