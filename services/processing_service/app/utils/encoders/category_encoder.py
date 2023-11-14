import numpy as np
import pandas as pd


from models import EncodeTypes
from utils.encoders import Encoder


class CategoryEncoder(Encoder):

    NAME = EncodeTypes.CATEGORY.value

    def __init__(self, s3_service, key, encoder_data=None):
        self.s3_service = s3_service
        self.key = key

        if encoder_data is None:
            self.categories = None
        else:
            self.categories = pd.api.types.CategoricalDtype(
                encoder_data.get('categories')
            )

    def __call__(self, df):
        if self.categories is None:
            df = df.astype('category')
            self.categories = pd.api.types.CategoricalDtype(df.cat.categories)
        else:
            df = df.astype(self.categories)

        return np.array(df.cat.codes, dtype="int64")

    async def update(self):
        await self._update({'categories': self.categories.categories.tolist()})
