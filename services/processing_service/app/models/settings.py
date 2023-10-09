from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    aws_access_key_id: str
    aws_secret_access_key: str
    util_s3_path: str = "http://s3:9000"
    util_bucket: str

    chunk_size: int

    encoders_data_key: str
