from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    num_search_trials: int
    batch_size: int
    ml_device: str

    aws_access_key_id: str
    aws_secret_access_key: str
    chunk_size: int
    util_bucket: str
    util_dir_s3_key: str
    create_endpoint_url: str
    model_key_map: dict = {
        "SAGE": "models/SAGE.bin"
    }
