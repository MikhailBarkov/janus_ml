from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

from models import EncodeTypes
from utils.encoders import Encoder


class BOWEncoder(Encoder):

    NAME = EncodeTypes.BOW.value

    def __init__(self, s3_service, key, encoder_data=None):
        self.s3_service = s3_service
        self.key = key

        if encoder_data is None:
            self.vectorizer = None
        else:
            self.vectorizer = CountVectorizer(
                stop_words='english',
                vocabulary=encoder_data.get('vocabulary'),
                max_df=0.2,
                min_df=0.01,
                max_features=256
            )

    def __call__(self, df):
        if self.vectorizer is None:
            self.vectorizer = CountVectorizer(
                stop_words='english',
                max_df=0.2,
                min_df=0.01,
                max_features=256
            )

        matrix = self.vectorizer.fit_transform(df)
        return np.array(matrix.toarray(), dtype='float32')

    async def update(self):
        await self._update(
            {'vocabulary': self.vectorizer.get_feature_names_out().tolist()}
        )
