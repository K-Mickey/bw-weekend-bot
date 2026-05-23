import shutil
from pathlib import Path
from typing import Callable

import pytest

from scripts.validate_content import (
    check_domain_objects,
    check_node_ids,
    check_target_exists,
    get_files,
    load_files,
    main,
)


@pytest.fixture
def copy_yaml_to_tmp(tmp_path: Path) -> Callable[[list[Path]], Path]:
    def _inner(sources: list[Path]) -> Path:
        dest_root = tmp_path / "content" / "data"
        dest_root.mkdir(parents=True, exist_ok=True)
        for src in sources:
            shutil.copy(src, dest_root / src.name)
        return tmp_path

    return _inner


def test_get_files(root_dir: Path, data_dir: Path):
    files = get_files(root_dir)
    expected_count = len(list(data_dir.glob("*.yaml")))
    assert len(files) == expected_count


def test_load_files(root_dir: Path):
    files = get_files(root_dir)
    loaded = load_files(files)
    assert len(loaded) == len(files)
    for data in loaded:
        assert isinstance(data, (dict, list))


def test_check_node_ids_success(get_test_data):
    nodes_list = get_test_data("node_ids_ok.yaml")
    assert check_node_ids(tuple(nodes_list)) == 0


def test_check_node_ids_failure(get_test_data):
    nodes_list = get_test_data("node_ids_dup.yaml")
    assert check_node_ids(tuple(nodes_list)) == 1


def test_check_target_exists_success(get_test_data):
    nodes_list = get_test_data("target_ok.yaml")
    assert check_target_exists(tuple(nodes_list)) == 0


def test_check_target_exists_failure(get_test_data):
    nodes = get_test_data("menu_ok.yaml")
    assert check_target_exists((nodes,)) == 2


def test_check_domain_objects_success(get_test_data):
    node = get_test_data("valid_menu.yaml")
    assert check_domain_objects((node,)) == 0


def test_check_domain_objects_failure(get_test_data):
    node = get_test_data("invalid_mix.yaml")
    assert check_domain_objects((node,)) == 1


def test_main_success(data_dir: Path, copy_yaml_to_tmp):
    project_root = copy_yaml_to_tmp([data_dir / "valid_menu.yaml"])
    assert main(project_root) == 0


def test_main_failure_duplicate_id(data_dir: Path, copy_yaml_to_tmp):
    project_root = copy_yaml_to_tmp(
        [
            data_dir / "duplicate_a.yaml",
            data_dir / "duplicate_b.yaml",
        ]
    )
    assert main(project_root) == 1
