import pydantic


class S3Params(pydantic.BaseModel):
    bucket: str
    s3_endpoint_url: str


class CallRequest(pydantic.BaseModel):
    predict_entity_idx: int
    interface: str
    endpoint_id: str


class CreateRequest(pydantic.BaseModel):
    s3_key: str
