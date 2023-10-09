from enum import Enum


class EncodeTypes(Enum):
    CATEGORY = 'category'

    FLOAT_ARRAY = 'float_array'
    INT_ARRAY = 'int_array'

    BOW = 'bow'
    TFIDF = 'tfidf'
    HASH = 'hash'

    INT = 'int'
    FLOAT = 'float'
