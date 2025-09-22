from dataclasses import dataclass
from typing import Tuple
from ..domain.entities import AuthAttempt, UserProfile
from ..domain.value_objects import IPAddress, DeviceFingerprint, GeoPoint
from ..domain.policies import DecisionPolicy
from ..domain.services import RiskEngine
from ..domain.repositories import UserProfileRepository, RiskEventRepository


@dataclass
class EvaluateLoginAttempt:
    profiles: UserProfileRepository
    events: RiskEventRepository
    engine: RiskEngine
    policy: DecisionPolicy
    ctx: object

    def handle(self, cmd) -> Tuple[str, float, list]:
        attempt = AuthAttempt(cmd.user_id, cmd.ts, IPAddress(cmd.ip), DeviceFingerprint(cmd.device),
                              GeoPoint(cmd.lat, cmd.lon), cmd.country)
        profile = self.profiles.get(cmd.user_id) or UserProfile(cmd.user_id)
        self.profiles.save(profile)
        risk = self.engine.score(profile, attempt, self.ctx)
        decision = self.policy.decide(risk)
        if cmd.success is True and decision == "ALLOW":
            profile.register_success(cmd.ts, attempt.geo, attempt.device, attempt.country)
            self.profiles.save(profile)
        elif cmd.success is False:
            profile.register_failure(cmd.ts)
            self.profiles.save(profile)
        return decision, risk.value, [r.code for r in risk.reasons]