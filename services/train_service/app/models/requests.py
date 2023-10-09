from typing import Optional

import pydantic


class S3Params(pydantic.BaseModel):
    bucket: str
    s3_endpoint_url: str


class TrainParams(pydantic.BaseModel):
    s3_params: S3Params
    train_config_s3_key: str
    processing_config_s3_key: str
    model_hpo_config_s3_key: Optional[str] = None
