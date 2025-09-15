from dataclasses import dataclass, field
from typing import Optional, List, Set
from .value_objects import GeoPoint, IPAddress, DeviceFingerprint


@dataclass
class UserProfile:
    user_id: str
    known_devices: Set[str] = field(default_factory=set)
    typical_hours: Set[int] = field(default_factory=set)
    last_geo: Optional[GeoPoint] = None
    last_login_ts: Optional[float] = None
    failed_attempts_window: List[float] = field(default_factory=list)
    country_history: Set[str] = field(default_factory=set)

    def register_success(self, ts: float, geo: Optional[GeoPoint], device: Optional[DeviceFingerprint],
                         country: Optional[str] = None):
        if device: self.known_devices.add(device.value)
        if geo: self.last_geo = geo
        if country: self.country_history.add(country)
        self.last_login_ts = ts
        hour = int(ts % 86400) // 3600
        self.typical_hours.add(hour)
        self.failed_attempts_window.clear()

    def register_failure(self, ts: float):
        self.failed_attempts_window.append(ts)
        if len(self.failed_attempts_window) > 20:
            self.failed_attempts_window = self.failed_attempts_window[-20:]


@dataclass
class AuthAttempt:
    user_id: str
    ts: float
    ip: IPAddress
    device: DeviceFingerprint
    geo: GeoPoint
    country: str
