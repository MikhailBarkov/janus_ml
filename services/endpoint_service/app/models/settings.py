from typing import Dict

from pydantic import (
    BaseModel,
    conint
)
from pydantic_settings import BaseSettings


class JanusEndpointParams(BaseModel):
    endpoint: str = 'ws://janusgraph:8182/gremlin'


class Settings(BaseSettings, case_sensitive=False):
    util_s3_path: str
    util_bucket: str

    endpoints_config_s3_key: str

    janus_endpoint_params: JanusEndpointParams = JanusEndpointParams()

    export_service_url: str
    processing_service_url: str

    chunk_size: conint(ge=1)

    aws_access_key_id: str
    aws_secret_access_key: str

    model_key_map: Dict[str, str]
