import asyncio

import aiohttp
import torch
import datetime

from services.s3_service import S3Service
from settings import config
from utils.temp.sage import SAGE

class Endpoint:

    @classmethod
    async def load(cls, s3_key):
        s3_service = S3Service(config.util_s3_path)

        params = await s3_service.load_json(s3_key, config.util_bucket)
        Model = SAGE
        state = await s3_service.load_state(params['model_s3_key'])

        return Endpoint(s3_service, params, state, Model)

    def __init__(self, s3_service, params, state, Model):
        self.s3_service = s3_service
        self.name = params['train_config']['name']
        self.params = params
        self.model = Model(**params['hyperparameters'])

        self.model.load_state_dict(state)
        # self.code_label_map = params['proc_config']['node_categories_map']['label']

    async def call(self, entity_id, interface):
        graph, entity_id = await self.load_graph(entity_id, interface)
        pred = self.predict(entity_id, graph)
        return pred

    def predict(self, entity_id, graph):
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(graph, graph.ndata['feat']).tolist()

        return prediction[entity_id].index(max(prediction[entity_id]))

    async def load_graph(self, entity_id, interface):
        train_config = self.params['train_config']
        train_config.update(
            {
                "entity_id": entity_id,
                "interface": interface,
                "n_layers": self.params['hyperparameters']['n_layers']
            }
        )
        export_resp = await self.export(train_config)
        export_resp = export_resp['jobs'][0]

        processed_data_s3_location = 'temp_path'
        await self.processing(export_resp, processed_data_s3_location)

        graph = await self.s3_service.load_graph(
            f"{processed_data_s3_location}/{train_config['name']}.bin",
            config.util_bucket
        )

        return graph, export_resp['entity_id']

    async def export(self, export_params):
        request_json = {
            "output_s3_path": config.util_s3_path,
            "bucket": config.util_bucket,
            "params": config.janus_endpoint_params.model_dump(),
            "additional_params": {
                "jobs": [export_params]
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.export_service_url, json=request_json
            ) as resp:
                return await resp.json(content_type=None)

    async def processing(self, export_resp, processed_data_s3_location):
        request_json = {
            "s3_endpoint_url": config.util_s3_path,
            "bucket": config.util_bucket,
            "job_path": export_resp['job_s3_key'],
            "processed_data_s3_location": processed_data_s3_location,
            "config_file_name": export_resp['config_file_name']
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.processing_service_url, json=request_json
            ) as resp:
                return await resp.json(content_type=None)
