from utils.encoders import TypeEncoder
from models import EncodeTypes


class FloatEncoder(TypeEncoder):

    NAME = EncodeTypes.FLOAT.value
    DTYPE = 'float32'
