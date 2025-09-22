from dataclasses import dataclass
from .geoip import GeoService
from .ip_reputation import IPReputation


@dataclass
class Context: geo: GeoService; iprep: IPReputation
