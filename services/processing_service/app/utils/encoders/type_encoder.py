class TypeEncoder:

    DTYPE = 'float32'

    @classmethod
    async def load(cls, *args, **kwargs):
        return cls()

    @classmethod
    def create(cls):
        return cls()

    def __call__(self, df):
        return np.array(df, dtype=self.DTYPE)

    async def update(self, *args, **kwargs):
        pass
