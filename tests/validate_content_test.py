from pathlib import Path

import pytest

from scripts.validate_content import (
    check_available_from_dates,
    check_node_ids,
    check_target_exists,
    get_files,
    load_files,
)


@pytest.fixture
def yaml_file(tmp_path: Path) -> Path:
    data_dir = tmp_path / "content" / "data"
    data_dir.mkdir(parents=True)
    p = data_dir / "test.yaml"
    p.write_text("id: test\nvalue: 42", encoding="utf-8")
    return p


def test_get_files(tmp_path: Path, yaml_file: Path):
    files = get_files(tmp_path)
    assert yaml_file in files


def test_check_node_ids(tmp_path: Path):
    nodes = [{"id": "a"}, {"id": "b"}]
    assert check_node_ids(tuple(nodes)) == 0
    nodes_dup = [{"id": "a"}, {"id": "a"}]
    assert check_node_ids(tuple(nodes_dup)) == 1


def test_check_target_exists(tmp_path: Path):
    nodes = [{"id": "a", "keyboard": [{"target": "b"}]}, {"id": "b"}]
    assert check_target_exists(tuple(nodes)) == 0
    nodes_bad = [{"id": "a", "keyboard": [{"target": "c"}]}]
    assert check_target_exists(tuple(nodes_bad)) == 1


def test_check_available_from_dates(tmp_path: Path):
    nodes = [{"id": "a", "available_from": "2023-01-01"}]
    assert check_available_from_dates(tuple(nodes)) == 0
    nodes_bad = [{"id": "b", "available_from": "not-a-date"}]
    assert check_available_from_dates(tuple(nodes_bad)) == 1


def test_load_files(tmp_path: Path, yaml_file: Path):
    yaml_paths = get_files(tmp_path)
    loaded = load_files(yaml_paths)

    file = loaded[0]
    assert "test" in file.get("id")
    assert file.get("value") == 42
