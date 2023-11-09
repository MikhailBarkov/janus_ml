from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    root_s3_key_name: str

    aws_access_key_id: str
    aws_secret_access_key: str

    chunk_size: int

    janusgraph_pool_size: int
    jasnugraph_max_content_length: int
    janusgraph_batch_size: int
