from pathlib import Path
from json import load

from models import Settings


BASE_DIR = Path(__file__).parent.parent
hpo_config_path = BASE_DIR / 'config' / 'model-HPO-configuration.json'


def get_config():
    return Settings()


def get_hpo_config(path: Path):
    with open(path) as rf:
        config = load(rf)
    return config


config = Settings()
default_hpo_config = get_hpo_config(hpo_config_path)
