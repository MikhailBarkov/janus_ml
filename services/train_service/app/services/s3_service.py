import json
import os
import tempfile
import io
import pickle

import aioboto3
import dgl
import torch

from models import S3Params
from s3 import S3Client
from settings import config


class S3Service:

    def __init__(self, s3_params: S3Params):
        self.s3_client = S3Client(s3_params.s3_endpoint_url)
        self.bucket = s3_params.bucket
        self.util_bucket = config.util_bucket

    async def load_json(self, key):
        text = await self.load_text(key)
        return json.loads(text)

    async def load_dataset(self, key):
        graph_bytes = await self.load_text(key)

        _, filename = tempfile.mkstemp()
        with open(filename, 'wb') as wf:
            wf.write(graph_bytes)

        return dgl.load_graphs(filename)[0]

    async def load_text(self, key, bucket=None, chunk_size=config.chunk_size):
        if bucket is None:
            bucket = self.bucket

        async with self.s3_client() as s3:
            s3_obj = await s3.get_object(
                Bucket=bucket,
                Key=key
            )

            stream = s3_obj["Body"]
            batches = []
            while txt := await stream.read(chunk_size):
                batches.append(txt)

        return b''.join(batches)

    async def upload_model(self, model, model_s3_key):
        buff = io.BytesIO()
        torch.save(model, buff)
        async with self.s3_client() as s3:
            await s3.upload_fileobj(io.BytesIO(buff.getvalue()), self.util_bucket, model_s3_key)

    async def upload_json(self, file_dict, s3_key):
        buff = io.StringIO()
        json.dump(file_dict, buff)

        async with self.s3_client() as s3:
            await s3.upload_fileobj(io.BytesIO(buff.getvalue().encode()), self.util_bucket, s3_key)

    async def load_model(self, model_name):
        model_key = config.model_key_map[model_name]
        model_bytes = await self.load_text(model_key, bucket=config.util_bucket)

        buff = io.BytesIO(model_bytes)

        return torch.load(buff)
