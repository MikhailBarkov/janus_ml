import pydantic


class ProcParams(pydantic.BaseModel):
    s3_endpoint_url: str
    bucket: str
    job_path: str
    processed_data_s3_location: str
    config_file_name: str
