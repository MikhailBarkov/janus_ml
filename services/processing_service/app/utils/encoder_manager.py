from models import EncodeTypes
from utils.encoders import (
    CategoryEncoder,
    FloatArrayEncoder,
    IntArrayEncoder,
    FloatEncoder,
    IntEncoder,
    BOWEncoder,
    TFIDFEncoder,
    HashEncoder
)

class EncoderManager:

    ENCODERS_MAP = {
        EncodeTypes.CATEGORY.value: CategoryEncoder,
        EncodeTypes.FLOAT_ARRAY.value: FloatArrayEncoder,
        EncodeTypes.INT_ARRAY.value: IntArrayEncoder,
        EncodeTypes.BOW.value: BOWEncoder,
        EncodeTypes.TFIDF.value: TFIDFEncoder,
        EncodeTypes.HASH.value: HashEncoder,
        EncodeTypes.INT.value: IntEncoder,
        EncodeTypes.FLOAT.value: FloatEncoder,
    }

    @classmethod
    def get_encoder_class(cls, encode_type):
        try:
            return cls.ENCODERS_MAP[encode_type]
        except BaseException as e:
            raise ValueError(str(e) + str(cls.ENCODERS_MAP) + encode_type)
