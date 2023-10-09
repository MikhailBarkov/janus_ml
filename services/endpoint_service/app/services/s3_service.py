import json
import io
import pickle
import tempfile

import aioboto3
import torch
import dgl

from models import S3Params
from s3 import S3Client
from settings import config


class S3Service:

    def __init__(self, s3_endpoint_url):
        self.s3_client = S3Client(s3_endpoint_url)

    async def load_model(self, model_name):
        model_key = config.model_key_map[model_name]
        model_bytes = self.load_text(model_key, config.util_bucket)

        return pickle.loads(model_bytes)

    async def load_state(self, state_url):
        state = await self.load_text(state_url, config.util_bucket)
        buff = io.BytesIO(state)
        return torch.load(buff)

    async def load_json(self, key, bucket):
        text = await self.load_text(key, bucket)
        return json.loads(text)

    async def load_text(self, key, bucket, chunk_size=config.chunk_size):
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

    async def upload_json(self, file_dict, key, bucket):
        buff = io.StringIO()
        json.dump(file_dict, buff)

        async with self.s3_client() as s3:
            await s3.upload_fileobj(io.BytesIO(buff.getvalue().encode()), bucket, key)

    async def load_graph(self, key, bucket):
        graph_bytes = await self.load_text(key, bucket)

        _, filename = tempfile.mkstemp()
        with open(filename, 'wb') as wf:
            wf.write(graph_bytes)

        glist, _ = dgl.load_graphs(filename)

        return glist[0]
