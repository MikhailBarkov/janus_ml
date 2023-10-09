import asyncio

from utils.endpoint import Endpoint
from services import S3Service
from models import S3Params
from settings import config


class EndpointService:

    @classmethod
    async def create(cls):
        self = EndpointService()

        if not hasattr(cls, 'endpoints'):
            endpoints = await self.load_endpoints()

            self.endpoints = {
                endpoint.name: endpoint for endpoint in endpoints
            }

        return self

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EndpointService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.s3_service = S3Service(config.util_s3_path)

    async def load_endpoints(self):
        try:
            self.endpoints_config = await self.s3_service.load_json(
                config.endpoints_config_s3_key, config.util_bucket,
            )
        except BaseException:
            await self.s3_service.upload_json(
                {'endpoints_s3_keys': []}, config.endpoints_config_s3_key, config.util_bucket
            )
            self.endpoints_config = {'endpoints_s3_keys': []}

        if len(self.endpoints_config['endpoints_s3_keys']) == 0:
            return []

        return await asyncio.gather(
            *[Endpoint.load(key) for key in self.endpoints_config['endpoints_s3_keys']]
        )

    async def create_endpoint(self, endpoint_config):
        endpoint = await Endpoint.load(endpoint_config.s3_key)

        self.endpoints[endpoint.name] = endpoint

        if not (endpoint_config.s3_key in self.endpoints_config['endpoints_s3_keys']):
            self.endpoints_config['endpoints_s3_keys'].append(
                endpoint_config.s3_key
            )

        await self.s3_service.upload_json(
            self.endpoints_config,
            config.endpoints_config_s3_key,
            config.util_bucket,
        )

        return

    async def call(self, call_params):
        endpoint = self.endpoints.get(call_params.endpoint_id)
        if endpoint is None:
            raise ValueError(f'Endpoint with id {call_params.endpoint_id} not found')

        return await endpoint.call(
            call_params.predict_entity_idx, interface=call_params.interface
        )




