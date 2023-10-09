from utils.encoders import TypeEncoder
from models import EncodeTypes


class IntEncoder(TypeEncoder):

    NAME = EncodeTypes.INT.value
    DTYPE = 'int64'
