from sklearn.feature_extraction.text import HashingVectorizer
import numpy as np

from models import EncodeTypes
from utils.encoders import Encoder


class HashEncoder(Encoder):

    NAME = EncodeTypes.HASH.value

    def __init__(self, s3_service, key, encoder_data=None):
        self.s3_service = s3_service
        self.key = key

        if encoder_data is None:
            self.vectorizer = None
        else:
            self.vectorizer = HashingVectorizer(
                stop_words='english',
                n_features=512
            )

    def __call__(self, df):
        if self.vectorizer is None:
            self.vectorizer = HashingVectorizer(
                stop_words='english',
                n_features=512
            )

        matrix = self.vectorizer.fit_transform(df)
        return np.array(matrix.toarray(), dtype='float64')

    async def update(self):
        pass
