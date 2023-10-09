import numpy as np


class ArrayEncoder:

    DTYPE = 'float32'

    @classmethod
    async def load(cls, *args, **kwargs):
        return cls()

    @classmethod
    def create(cls):
        return cls()

    def __call__(self, df):
        return np.array(
            [
                np.fromstring(
                    row.lstrip('[').rstrip(']'), dtype=self.DTYPE, sep=', '
                ) for row in df
            ],
        )

    async def update(self, *args, **kwargs):
        pass
