#!/usr/bin/env -S uv run --script
"""
Refactored content validation script.
All user‑facing messages are in English and emitted through the standard logging module.
The script performs three independent checks on the YAML files placed in ``content/data``:

1. **Unique node IDs** – each file must contain an ``id`` field and the values must be unique.
2. **Target existence** – every ``target`` referenced in a ``keyboard`` entry must point to an existing ``id``.
3. **Valid ``available_from`` date** – when present, the value must be an ISO‑8601 date string.

The module is deliberately split into small, pure functions to make unit testing trivial.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from ruamel.yaml import YAML

log = logging.getLogger(__name__)


def get_files(root: Path) -> tuple[Path, ...]:
    """Return a sorted tuple of all ``*.yaml`` files under ``root/content/data``.

    Parameters
    ----------
    root: Path
        Project root directory (usually ``Path(__file__).parents[2]``).
    """
    data_dir = root / "content" / "data"
    return tuple(sorted(data_dir.rglob("*.yaml")))


def _load_yaml(file_path: Path) -> dict | None:
    """Parse a single yaml file.

    Returns the parsed dictionary on success or ``None`` if parsing fails.
    Errors are logged with ``log.error``.
    """
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            data = YAML(typ="safe").load(fh) or {}
            return data
    except Exception as exc:  # includes YAMLError and IO errors
        log.error("Failed to parse %s – %s", file_path, exc)
        return None


def load_files(files: tuple[Path, ...]) -> tuple[dict, ...]:
    """Parse each path once and return a tuple containing only successfully loaded dicts."""
    loaded: list[dict] = []
    for fp in files:
        data = _load_yaml(fp)
        if data is not None:
            loaded.append(data)
    return tuple(loaded)


def check_node_ids(nodes: tuple[dict, ...]) -> int:
    """Validate that every node defines a unique ``id`` field.
    Returns the count of detected errors.
    """
    seen: set[str] = set()
    errors = 0
    for node in nodes:
        nid = node.get("id")
        if not nid:
            log.error("Node missing required field `id`: %s", node)
            errors += 1
            continue
        if nid in seen:
            log.error("Duplicate node id `%s` found", nid)
            errors += 1
        else:
            seen.add(nid)
    return errors


def check_target_exists(nodes: tuple[dict, ...]) -> int:
    """Ensure each button ``target`` references an existing node ``id``.
    Returns the number of broken references.
    """
    valid_ids = {n.get("id") for n in nodes if n.get("id")}
    errors = 0
    for node in nodes:
        for btn in node.get("keyboard", []):
            target = btn.get("target")
            if target and target not in valid_ids:
                log.error(
                    "Node `%s` contains unknown target `%s`",
                    node.get("id"),
                    target,
                )
                errors += 1
    return errors


def check_available_from_dates(nodes: tuple[dict, ...]) -> int:
    """Validate ISO‑8601 format of ``available_from`` values.
    Returns the number of malformed dates.
    """
    errors = 0
    for node in nodes:
        af = node.get("available_from")
        if af:
            try:
                datetime.fromisoformat(af)
            except ValueError:
                log.error(
                    "Node `%s` has invalid `available_from` value `%s`",
                    node.get("id"),
                    af,
                )
                errors += 1
    return errors


def main() -> int:
    """Run the full validation pipeline.
    Returns ``0`` on success, ``1`` when any validation error is found.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    project_root = Path(__file__).parents[2]
    if not project_root.exists():
        log.error("Project root directory does not exist: %s", project_root)
        return 0
    yaml_files = get_files(project_root)
    if not yaml_files:
        log.info("No yaml files found – nothing to validate.")
        return 0

    nodes = load_files(yaml_files)

    total_errors = 0
    total_errors += check_node_ids(nodes)
    total_errors += check_target_exists(nodes)
    total_errors += check_available_from_dates(nodes)

    if total_errors:
        log.error("%d validation error(s) found.", total_errors)
        return 1
    else:
        log.info("All yaml files passed validation.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
