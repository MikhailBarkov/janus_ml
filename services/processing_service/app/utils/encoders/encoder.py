from settings import config
from services import S3Service


class Encoder:

    @classmethod
    async def load(cls, job_name: str, property: str):
        s3_service = S3Service(
            config.util_s3_path,
            config.util_bucket,
            config.encoders_data_key + job_name
        )

        key = f'{config.encoders_data_key}/{job_name}/{cls.NAME}_{property}.json'

        try:
            encoder_data = await s3_service.load_json(key)
        except BaseException as e:
            encoder_data = None

        return cls(s3_service, key, encoder_data=encoder_data)

    @classmethod
    def create(cls, job_name: str, property: str):
        s3_service = S3Service(
            config.util_s3_path,
            config.util_bucket,
            config.encoders_data_key + job_name
        )

        key = f'{cls.NAME}_{property}.json'

        return cls(s3_service, key)

    async def _update(self, data: dict):
        await self.s3_service.upload_json(data, self.key)
