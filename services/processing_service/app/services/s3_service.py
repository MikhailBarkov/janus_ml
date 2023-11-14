import tempfile
import os
import io
import json
from itertools import chain
import asyncio

from dgl import save_graphs
import yaml

from s3 import S3Client
from settings import config


class S3Service:

    def __init__(self, s3_endpoint_url: str, bucket: str, job_path: str):
        self.s3_client = S3Client(s3_endpoint_url)
        self.bucket = bucket
        self.job_path = job_path

    async def load_data(self) -> str:
        root_dir = tempfile.mkdtemp()

        meta_yaml = await self.load_text(os.path.join(self.job_path, 'meta.yaml'))

        meta = yaml.load(meta_yaml, yaml.Loader)
        nodes, edges = meta.get('node_data', ()), meta.get('edge_data', ())
        nodes_coro = [
            self.load_file(root_dir, node['file_name']) for node in nodes
        ]
        edges_coro = [
            self.load_file(root_dir, edge['file_name']) for edge in edges
        ]

        names = await asyncio.gather(*list(nodes_coro + edges_coro))
        for field, name in zip(chain(nodes, edges), names):
            field['file_name'] = name

        meta_str = yaml.dump(meta)

        _, meta_path = tempfile.mkstemp(suffix='.yaml', prefix='meta', dir=root_dir)
        with open(os.path.join(root_dir, meta_path), 'w') as wf:
            wf.write(meta_str)

        _, meta_path = os.path.split(meta_path)
        return root_dir, meta_path

    async def load_file(
        self, root_dir: tempfile.TemporaryDirectory, file_name: str
    ) -> str:
        file_text = await self.load_text(
            os.path.join(self.job_path, file_name)
        )

        _, path = tempfile.mkstemp(suffix=file_name, prefix='', dir=root_dir)
        with open(os.path.join(root_dir, path), 'wb') as wf:
            wf.write(file_text)

        _, path = os.path.split(path)
        return path

    async def load_text(self, key, chunk_size=config.chunk_size):
        async with self.s3_client() as s3:
            s3_obj = await s3.get_object(
                Bucket=self.bucket,
                Key=key
            )
            stream = s3_obj["Body"]
            batches = []
            while txt := await stream.read(chunk_size):
                batches.append(txt)

        return b''.join(batches)

    async def load_json(self, key):
        text = await self.load_text(key)
        return json.loads(text)

    async def upload_dataset(
        self,
        dataset,
        key: str
    ):
        _, dataset_file = tempfile.mkstemp()
        save_graphs(dataset_file, dataset[0])

        async with self.s3_client() as s3:
            await s3.upload_fileobj(
                open(dataset_file, 'rb'),
                self.bucket,
                key
            )

    async def upload_json(self, json_dict, key):
        buff = io.StringIO()
        json.dump(json_dict, buff)

        async with self.s3_client() as s3:
            await s3.upload_fileobj(
                io.BytesIO(buff.getvalue().encode()),
                self.bucket,
                key,
            )
