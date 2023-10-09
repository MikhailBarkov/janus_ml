import asyncio
from collections import defaultdict
from typing import Union, List

from gremlin_python.process.traversal import T

from services.load_service import LoadService
from services.s3_service import S3Service
from settings import config
from models import (
    BaseTarget,
    BaseFeature,
    Interface,
    UserJob,
    UtilJob
)


class ExportService:

    @classmethod
    async def create(cls, export_params):
        self = ExportService(export_params)
        self.load_service = await LoadService.create(export_params.params.endpoint)
        return self

    def __init__(self, export_params):
        self.params = export_params
        self.s3_service = S3Service(
            export_params.output_s3_path,
            export_params.bucket
        )

    async def export(self):
        jobs = await self.do_jobs(self.params.additional_params.jobs)
        return {'jobs': jobs}

    async def do_jobs(self, jobs: List[Union[UserJob, UtilJob]]):
        job_coroutines = [
            self.do_job(job) for job in self.params.additional_params.jobs
        ]
        responses = await asyncio.gather(*job_coroutines)

        return responses

    async def do_job(self, job: Union[UserJob, UtilJob]):
        job_key = f'{config.root_s3_key_name}/{job.name}'

        nodes_params, edges_params, meta_params = self.parse_job(job)

        if isinstance(job, UserJob):
            await asyncio.gather(
                self.export_nodes(nodes_params, job_key),
                self.export_edges(edges_params, job_key),
                self.s3_service.upload_meta(meta_params, job_key),
                self.s3_service.upload_train_config(job, job_key)
            )

            return {
                'job_s3_key': job_key,
                'config_file_name': 'train_config.json',
            }

        elif isinstance(job, UtilJob) and job.interface == Interface.TRANSDUCTIVE:
            nodes, edges, _, _ = await asyncio.gather(
                self.export_nodes(nodes_params, job_key),
                self.export_edges(edges_params, job_key),
                self.s3_service.upload_meta(meta_params, job_key),
                self.s3_service.upload_train_config(job, job_key),
            )

            for i, n in enumerate(nodes):
                if n['node_id'] == job.entity_id:
                    new_entity_id = i
                    break
            else:
                raise ValueError(f'{job.entity_id} not found')

            return {
                'job_s3_key': job_key,
                'config_file_name': 'train_config.json',
                'entity_id': new_entity_id
            }

        else:
            new_entity_id, _, _ = await asyncio.gather(
                self.inductive_load(
                    nodes_params, edges_params, job.n_layers, job.entity_id, job_key
                ),
                self.s3_service.upload_meta(meta_params, job_key),
                self.s3_service.upload_train_config(job, job_key),
            )

            return {
                'job_s3_key': job_key,
                'config_file_name': 'train_config.json',
                'entity_id': new_entity_id
            }

    def parse_job(self, job: Union[UserJob, UtilJob]):
        nodes_params, edges_params = defaultdict(list), defaultdict(list)

        if job.target.node:
            nodes_params[job.target.node].append(job.target.property)
        else:
            edges_params[job.target.edge].append(job.target.property)

        for feature in job.features:
            if feature.node:
                nodes_params[feature.node].append(feature.property)
            else:
                edges_params[feature.edge].append(feature.property)

        meta_params = {
            'job_name': job.name,
            'nodes_labels': list(nodes_params.keys()),
            'edges_labels': list(edges_params.keys())
        }

        return nodes_params, edges_params, meta_params

    async def export_nodes(self, nodes_params: dict[list[str]], job_key):
        nodes_list = []

        for label, properties in nodes_params.items():
            nodes = await self.load_service.load_nodes(label, properties)

            await self.s3_service.upload_nodes(job_key, nodes, label, properties)

            nodes_list.append(nodes)

        return nodes_list[0]

    async def export_edges(self, edges_params, job_key):
        edges_list = []

        for label, properties in edges_params.items():
            edges = await self.load_service.load_edges(label, properties)

            await self.s3_service.upload_edges(job_key, edges, label, properties)

            edges_list.append(edges)

        return edges_list[0]

    async def inductive_load(
        self, nodes_params, edges_params, n_layers: int, entity_id, job_key: str
    ):
        for edge, properties in edges_params.items():
            nodes, edges = await self.load_service.inductive_load(
                entity_id, nodes_params, edge, properties, n_layers
            )

            #TODO: change when the model RGCN appears
            await asyncio.gather(
                self.s3_service.upload_nodes(job_key, nodes, edge.out, list(nodes_params.values())[0]),
                self.s3_service.upload_edges(job_key, edges, edge, properties)
            )

            for i, n in enumerate(nodes):
                if n['node_id'] == entity_id:
                    new_entity_id = i
                    break
            else:
                raise ValueError(f'{entity_id} not found')

        return new_entity_id
