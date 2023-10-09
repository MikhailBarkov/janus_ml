import numpy as np
import pandas as pd

from models import EncodeTypes


class DataParser:

    def __init__(self, encoders):
        self.encoders = encoders

    def __call__(self, df: pd.DataFrame):
        return {header: self.parse_header(header, df) for header in df}

    def parse_header(self, header, df: pd.DataFrame):
            if header == 'label':
                #TODO: Heterogenus graph
                pass
            elif header in self.encoders:
                encoder = self.encoders[header]
                return encoder(df[header])
            else:
                raise ValueError("Can't encode header" + header + str(self.encoders))

    def encode_label(self, df):
        category_code = max(self.categories_map['label'].keys()) + 1
        category_name = df[0]

        self.categories_map['label'][category_name] = category_code

        return df.replace(self.categories_map['label'])

    def category_encode(self, df):
        df = df.astype('category')

        #TODO: add categories_map

        return np.array(df.cat.codes, dtype="int64")

    def array_encode(self, df, dtype='float32'):
        dt = np.array(
            [np.fromstring(row.lstrip('[').rstrip(']'), dtype=dtype, sep=', ') for row in df]
        )
        return dt
