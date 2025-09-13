import json, os
from typing import Iterable, Optional, List
from ..domain.entities import UserProfile
from ..domain.repositories import UserProfileRepository, RiskEventRepository


class FileUserProfileRepository(UserProfileRepository):
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path): json.dump({}, open(self.path, "w"))

    def get(self, user_id: str) -> Optional[UserProfile]:
        data = json.load(open(self.path))
        d = data.get(user_id)
        if not d: return None
        up = UserProfile(user_id=user_id, known_devices=set(d.get("known_devices", [])),
                         typical_hours=set(d.get("typical_hours", [])),
                         country_history=set(d.get("country_history", [])))
        lg = d.get("last_geo")
        if lg: from ..domain.value_objects import GeoPoint; up.last_geo = GeoPoint(lg["lat"], lg["lon"])
        up.last_login_ts = d.get("last_login_ts")
        up.failed_attempts_window = d.get("failed_attempts_window", [])
        return up

    def save(self, profile: UserProfile) -> None:
        data = json.load(open(self.path))
        data[profile.user_id] = {
            "known_devices": list(profile.known_devices),
            "typical_hours": list(profile.typical_hours),
            "last_geo": ({"lat": profile.last_geo.lat, "lon": profile.last_geo.lon} if profile.last_geo else None),
            "last_login_ts": profile.last_login_ts,
            "failed_attempts_window": profile.failed_attempts_window,
            "country_history": list(profile.country_history)
        }
        json.dump(data, open(self.path, "w"), indent=2)


class MemoryEventRepository(RiskEventRepository):
    def __init__(self): self._events: List = []

    def append(self, e) -> None: self._events.append(e)

    def all(self) -> Iterable: return list(self._events)
