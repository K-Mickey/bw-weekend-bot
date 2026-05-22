from ruamel.yaml import YAML

from src.config import settings


def get_test_data(name: str):
    test_path = settings.test_content_data_dir
    full_path = test_path / name
    yaml = YAML(typ="safe")
    with full_path.open("r", encoding="utf-8") as f:
        return yaml.load(f)
