import asyncio
import os

from dgl.data import CSVDataset

from services import S3Service
from models import ProcParams, EncodeTypes
from utils import DataParser, EncoderManager
from s3 import S3Client


class ProcService:

    def __init__(self, proc_params: ProcParams):
        self.s3_service = S3Service(
            proc_params.s3_endpoint_url,
            proc_params.bucket,
            proc_params.job_path
        )
        self.proc_params = proc_params

    async def proc(self):
        config_file_s3_key = os.path.join(
            self.proc_params.job_path,
            self.proc_params.config_file_name
        )

        train_config, (root_dir, meta_yaml_file) = await asyncio.gather(
            self.s3_service.load_json(config_file_s3_key),
            self.s3_service.load_data()
        )

        n_encoders, e_encoders = await self.get_encoders(train_config)
        n_parser, e_parser = DataParser(n_encoders), DataParser(e_encoders)

        CSVDataset.META_YAML_NAME = str(meta_yaml_file)
        dataset = CSVDataset(
            root_dir,
            ndata_parser=n_parser,
            edata_parser=e_parser
        )

        await asyncio.gather(*[e.update() for e in n_encoders.values()])

        dataset_s3_key = os.path.join(
            self.proc_params.processed_data_s3_location,
            f'{dataset.name}.bin'
        )
        processing_config = self.prepare_dataset(
            dataset,
            train_config,
            dataset_s3_key,
        )
        upload_dataset_coro = self.s3_service.upload_dataset(
            dataset,
            dataset_s3_key,
        )
        upload_processing_config_coro = self.s3_service.upload_json(
            processing_config,
            os.path.join(
                self.proc_params.processed_data_s3_location,
                'processing_config.json'
            )
        )

        await asyncio.gather(upload_dataset_coro, upload_processing_config_coro)

        return processing_config

    async def get_encoders(self, train_config):
        n_encoders, e_encoders = {}, {}

        #TODO: change when tasks appear other than node classification
        encoder_cls = EncoderManager.get_encoder_class('category')

        if train_config.get('interface') == 'inductive':
            encoder = await encoder_cls.load(
                train_config.get('name'),
                train_config['target'].get('property')
            )
        else:
            encoder = encoder_cls.create(
                train_config.get('name'),
                train_config['target'].get('property')
            )

        n_encoders[train_config['target']['property']] = encoder

        for feature in train_config['features']:
            if feature.get('property'):
                encoder_cls = EncoderManager.get_encoder_class(
                    feature.get('type', 'category')
                )
                encoder = await encoder_cls.load(
                    train_config.get('name'),
                    feature.get('property')
                )

                if feature.get('node'):
                    n_encoders[feature.get('property')] = encoder
                else:
                    e_encoders[feature.get('property')] = encoder

        return n_encoders, e_encoders

    def prepare_dataset(
        self, dataset, train_config, dataset_s3_key
    ):
        if train_config['target']['type'] == 'classification' and train_config['target'].get('node'):
            self.prepare_node_classification(
                dataset,
                train_config['target'],
                train_config['features']
            )

        return {
            'processed_data_s3_location': dataset_s3_key,
        }


    def prepare_node_classification(self, dataset, target, features):
        graph = dataset[0]

        graph.ndata['label'] = graph.ndata[target['property']]
        graph.ndata['feat'] = graph.ndata[features[0]['property']]
