import asyncio

import aioboto3

from settings import config


class S3Client:

    def __init__(self, s3_endpoint_url: str):
        self.session = aioboto3.Session()
        self.s3_endpoint_url = s3_endpoint_url

    def __call__(self):
        return self.session.client(
            service_name='s3',
            endpoint_url=self.s3_endpoint_url,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key
        )
