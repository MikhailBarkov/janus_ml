import asyncio
import os

import aiohttp
from sklearn.model_selection import ParameterSampler

from services.s3_service import S3Service
from utils import (
    NodeClassificationTrainer,
    evaluate,
)
from utils.classification.sage import SAGE
from models import TrainParams
from settings import (
    config as app_config,
    default_hpo_config
)


class TrainService:

    def __init__(self, train_params: TrainParams):
        self.train_params = train_params
        self.s3_service = S3Service(train_params.s3_params)

    async def train(self):
        train_config, proc_config = await asyncio.gather(
            self.s3_service.load_json(self.train_params.train_config_s3_key),
            self.s3_service.load_json(self.train_params.processing_config_s3_key)
        )

        dataset, hyperparameters = await asyncio.gather(
            self.s3_service.load_dataset(proc_config['processed_data_s3_location']),
            self.get_hyperparameters(train_config),
        )

        best_model = await self._train(dataset, hyperparameters, train_config)
        model_s3_key = os.path.join(
            app_config.util_dir_s3_key, train_config['name'], 'model.bin'
        )

        model_config = {
            'train_config': train_config,
            'hyperparameters': best_model['hyperparameters'],
            'model_s3_key': model_s3_key,
            'proc_config': proc_config
        }
        model_config_s3_key = os.path.join(
            app_config.util_dir_s3_key, train_config['name'], 'model_config.json'
        )
        await asyncio.gather(
            self.s3_service.upload_model(best_model['model'], model_s3_key),
            self.s3_service.upload_json(model_config, model_config_s3_key)
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                app_config.create_endpoint_url,
                json={'s3_key': model_config_s3_key},
            ) as resp:
                endpoint_resp = await resp.json()

        # add resp with accuracy and s3_path params + more info
        return {'accuracy': best_model['accuracy']}

    async def _train(self, dataset, hyperparameters, train_config):

        configure_generator = ParameterSampler(
            hyperparameters, n_iter=app_config.num_search_trials
        )

        Model = await self.get_model_class(train_config)
        Trainer = self.get_trainer(train_config)

        best = {
            'model': None,
            'accuracy': 0,
            'hyperparameters': None
        }
        for config in configure_generator:
            trainer = Trainer(config, Model, split=train_config.get('split', [0.8, 0.1, 0.1]))
            model, params = trainer.fit(dataset)

            accuracy = evaluate(dataset, model)

            if accuracy > best['accuracy']:
                best['accuracy'] = accuracy
                best['model'] = model.state_dict()
                best['hyperparameters'] = params

        return best

    async def get_hyperparameters(self, train_config):
        hpo_config = default_hpo_config

        if self.train_params.model_hpo_config_s3_key:
            user_hpo_config = await self.s3_service.load_json(
                train_params.model_hpo_config_s3_key
            )
            hpo_config.update(user_hpo_config)

        return hpo_config

    def get_trainer(self, train_config):
        target = train_config['target']
        if target['type'] == 'classification' and target.get('node'):
            return NodeClassificationTrainer

    async def get_model_class(self, train_config):
        return SAGE
