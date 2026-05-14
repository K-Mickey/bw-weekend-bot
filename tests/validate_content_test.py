import shutil
from pathlib import Path
from typing import Callable, Union

import pytest
from ruamel.yaml import YAML

from scripts.validate_content import (
    check_domain_objects,
    check_node_ids,
    check_target_exists,
    get_files,
    load_files,
    main,
)


@pytest.fixture(scope="session")
def root_dir() -> Path:
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def yaml_dir(root_dir) -> Path:
    return root_dir / "content" / "data"


def load_yaml(path: Path) -> Union[dict, list]:
    yaml = YAML(typ="safe")
    with path.open("r", encoding="utf-8") as f:
        return yaml.load(f)


@pytest.fixture
def copy_yaml_to_tmp(tmp_path: Path) -> Callable[[list[Path]], Path]:
    def _inner(sources: list[Path]) -> Path:
        dest_root = tmp_path / "content" / "data"
        dest_root.mkdir(parents=True, exist_ok=True)
        for src in sources:
            shutil.copy(src, dest_root / src.name)
        return tmp_path

    return _inner


def test_get_files(root_dir: Path, yaml_dir: Path):
    files = get_files(root_dir)
    expected_count = len(list(yaml_dir.glob("*.yaml")))
    assert len(files) == expected_count


def test_load_files(root_dir: Path):
    files = get_files(root_dir)
    loaded = load_files(files)
    assert len(loaded) == len(files)
    for data in loaded:
        assert isinstance(data, (dict, list))


def test_check_node_ids_success(yaml_dir: Path):
    nodes_list = load_yaml(yaml_dir / "node_ids_ok.yaml")
    assert check_node_ids(tuple(nodes_list)) == 0


def test_check_node_ids_failure(yaml_dir: Path):
    nodes_list = load_yaml(yaml_dir / "node_ids_dup.yaml")
    assert check_node_ids(tuple(nodes_list)) == 1


def test_check_target_exists_success(yaml_dir: Path):
    nodes_list = load_yaml(yaml_dir / "target_ok.yaml")
    assert check_target_exists(tuple(nodes_list)) == 0


def test_check_target_exists_failure(yaml_dir: Path):
    nodes = [{"id": "a", "keyboard": [{"target": "c"}]}]
    assert check_target_exists(tuple(nodes)) == 1


def test_check_domain_objects_success(yaml_dir: Path):
    node = load_yaml(yaml_dir / "valid_menu.yaml")
    assert check_domain_objects((node,)) == 0


def test_check_domain_objects_failure(yaml_dir: Path):
    node = load_yaml(yaml_dir / "invalid_mix.yaml")
    assert check_domain_objects((node,)) == 1


def test_main_success(yaml_dir: Path, copy_yaml_to_tmp):
    project_root = copy_yaml_to_tmp([yaml_dir / "valid_menu.yaml"])
    assert main(project_root) == 0


def test_main_failure_duplicate_id(yaml_dir: Path, copy_yaml_to_tmp):
    project_root = copy_yaml_to_tmp(
        [
            yaml_dir / "duplicate_a.yaml",
            yaml_dir / "duplicate_b.yaml",
        ]
    )
    assert main(project_root) == 1
