from typing import Protocol, Optional, Iterable, List
from .entities import UserProfile


class UserProfileRepository(Protocol):
    def get(self, user_id: str) -> Optional[UserProfile]: ...

    def save(self, profile: UserProfile) -> None: ...


class RiskEventRepository(Protocol):
    def append(self, event) -> None: ...

    def all(self) -> Iterable: ...
