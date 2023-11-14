from models import EncodeTypes
from utils.encoders import ArrayEncoder


class FloatArrayEncoder(ArrayEncoder):

    NAME = EncodeTypes.FLOAT_ARRAY.value
    DTYPE = 'float32'
