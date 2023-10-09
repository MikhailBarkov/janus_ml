from models import EncodeTypes
from utils.encoders import ArrayEncoder


class IntArrayEncoder(ArrayEncoder):

    NAME = EncodeTypes.INT_ARRAY.value
    DTYPE = 'int64'
