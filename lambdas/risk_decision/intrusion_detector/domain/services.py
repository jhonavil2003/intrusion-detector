from dataclasses import dataclass
from typing import List, Sequence, Tuple
from .entities import UserProfile, AuthAttempt
from .value_objects import RiskScore, RiskReason


@dataclass
class RiskRule: code: str; weight: float


def _hour(ts: float) -> int: return int(ts % 86400) // 3600


class RiskEngine:
    def __init__(self, rules: Sequence[RiskRule]):
        self.rules: Tuple[RiskRule, ...] = tuple(rules)

    def score(self, profile: UserProfile, attempt: AuthAttempt, ctx) -> RiskScore:
        total = 0.0
        reasons: List[RiskReason] = []
        for rule in self.rules:
            ruleresult = rule.evaluate(profile, attempt, ctx)
            if ruleresult:
                reasons.append(ruleresult)
                total += max(0.0, ruleresult.score_delta)
        return RiskScore(value=max(0.0, min(100.0, total)), reasons=tuple(reasons))


class NewDeviceRule(RiskRule):
    def __init__(self, w=30.0): super().__init__('NEW_DEVICE', w)

    def evaluate(self, profile, attempt, ctx):
        if attempt.device.value not in profile.known_devices:
            return RiskReason(self.code, 'Dispositivo no reconocido', self.weight)
        return None


class UnusualHourRule(RiskRule):
    def __init__(self, w=20.0): super().__init__('UNUSUAL_HOUR', w)

    def evaluate(self, profile, attempt, ctx):
        h = _hour(attempt.ts)
        if profile.typical_hours and h not in profile.typical_hours:
            return RiskReason(self.code, f'Hora atípica: {h}', self.weight)
        return None


class ImpossibleTravelRule(RiskRule):
    def __init__(self, w=40.0, kmh=900.0):
        super().__init__('IMPOSSIBLE_TRAVEL', w);
        self.kmh = kmh

    def evaluate(self, profile, attempt, ctx):
        if profile.last_geo and profile.last_login_ts:
            km = ctx.geo.distance_km(profile.last_geo, attempt.geo)
            hours = max(0.001, (attempt.ts - profile.last_login_ts) / 3600.0)
            if km / hours > self.kmh:
                return RiskReason(self.code, 'Viaje imposible', self.weight)
        return None


class NewCountryRule(RiskRule):
    def __init__(self, w=25.0): super().__init__('NEW_COUNTRY', w)

    def evaluate(self, profile, attempt, ctx):
        if profile.country_history and attempt.country not in profile.country_history:
            return RiskReason(self.code, f'País nuevo: {attempt.country}', self.weight)
        return None


class FailedAttemptsRule(RiskRule):
    def __init__(self, w=10.0, recent=3): super().__init__('FAILED_STREAK', w); self.recent = recent

    def evaluate(self, profile, attempt, ctx):
        if len(profile.failed_attempts_window) >= self.recent:
            return RiskReason(self.code, 'Racha de fallos reciente', self.weight)
        return None


class BadIPRule(RiskRule):
    def __init__(self, w=35.0): super().__init__('BAD_IP', w)

    def evaluate(self, profile, attempt, ctx):
        if ctx.iprep.is_bad(attempt.ip.value):
            return RiskReason(self.code, 'IP mala reputación', self.weight)
        return None


class ASNChangeRule(RiskRule):
    def __init__(self, w=15.0): super().__init__('ASN_CHANGE', w)

    def evaluate(self, profile, attempt, ctx):
        last_asn = ctx.iprep.asn_for_profile(profile)
        cur_asn = ctx.iprep.asn(attempt.ip.value)
        if last_asn and cur_asn and last_asn != cur_asn:
            return RiskReason(self.code, f'Cambio ASN {last_asn}->{cur_asn}', self.weight)
        return None
