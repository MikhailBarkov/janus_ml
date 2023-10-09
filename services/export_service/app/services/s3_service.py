import io
import csv
import yaml
import json

from gremlin_python.process.traversal import T, Direction

from s3 import S3Client
from models import Edge


class S3Service:

    def __init__(self, output_s3_path, bucket):
        self.client = S3Client(output_s3_path)
        self.bucket = bucket

    async def upload_nodes(
        self, job_key: str, nodes: list[dict], label: str, properties: list[str]
    ):
        nodes_csv = self.nodes_to_csv(nodes, label, properties)
        file_name = f'{job_key}/nodes_{label}.csv'

        async with self.client() as s3:
            await s3.upload_fileobj(nodes_csv, self.bucket, file_name)

    async def upload_edges(
        self, job_key: str, edges: list[dict], label: Edge, properties: list[str]
    ):
        edges_csv = self.edges_to_csv(edges, label, properties)
        file_name = f'{job_key}/edges_{label.out}_{label.label}_{label.in_}.csv'

        async with self.client() as s3:
            await s3.upload_fileobj(edges_csv, self.bucket, file_name)

    async def upload_train_config(self, job, job_key):
        key = f'{job_key}/train_config.json'

        async with self.client() as s3:
            await s3.upload_fileobj(
                io.BytesIO(job.model_dump_json().encode()),
                self.bucket,
                key,
            )

    async def upload_meta(self, meta_params, job_key):
        meta_yaml = self.meta_to_yaml(meta_params)
        file_name = f'{job_key}/meta.yaml'

        async with self.client() as s3:
            await s3.upload_fileobj(meta_yaml, self.bucket, file_name)

    def nodes_to_csv(
        self, nodes: list[dict], label: str, properties: list[str]
    ) -> io.BytesIO:
        if not properties[0]:
            properties = []

        buff = io.StringIO()

        headers = ['node_id'] + properties
        writer = csv.DictWriter(buff, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()

        for node in nodes:
            for key, value in node.items():
                if type(value) is str:
                    node[key] = f'{value}'

            writer.writerow(node)

        return io.BytesIO(buff.getvalue().encode())

    def edges_to_csv(
        self, edges: list[dict], label, properties: list[str]
    ) -> io.BytesIO:
        if not properties[0]:
            properties = []

        buff = io.StringIO()

        headers = ['src_id', 'dst_id'] + properties
        writer = csv.DictWriter(buff, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()

        for edge in edges:
            for key, value in edge.items():
                if type(value) is str:
                    edge[key] = f'{value}'

            writer.writerow(edge)

        return io.BytesIO(buff.getvalue().encode())

    def meta_to_yaml(self, meta_params) -> io.BytesIO:
        buff = io.StringIO()

        to_yaml = {
            'dataset_name': meta_params['job_name'],
            'separator': ',',
            'edge_data': [
                {
                    'file_name': f'edges_{label.out}_{label.label}_{label.in_}.csv',
                    'etype': [label.out, label.label, label.in_]
                } for label in meta_params['edges_labels']
            ],
            'node_data': [
                {
                    'file_name': f'nodes_{label}.csv',
                    'ntype': label
                } for label in meta_params['nodes_labels']
            ]
        }

        yaml.dump(to_yaml, buff)

        return io.BytesIO(buff.getvalue().encode())
