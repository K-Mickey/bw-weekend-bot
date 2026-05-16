from typing import NamedTuple

from .network import Network


class UserKey(NamedTuple):
    network: Network
    external_id: str
