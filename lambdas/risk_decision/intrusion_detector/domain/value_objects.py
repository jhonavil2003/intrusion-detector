from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GeoPoint: lat: float; lon: float


@dataclass(frozen=True)
class IPAddress: value: str


@dataclass(frozen=True)
class DeviceFingerprint: value: str


@dataclass(frozen=True)
class RiskReason: code: str; message: str; score_delta: float


@dataclass(frozen=True)
class RiskScore: value: float; reasons: Tuple[RiskReason, ...]
