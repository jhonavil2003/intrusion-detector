from dataclasses import dataclass
from ..application.commands import EvaluateLoginCommand


@dataclass
class Topics:
    AUTH_ATTEMPTS = 'auth.attempts.v1'
    RISK_SCORES = 'risk.score.computed.v1'
    DECISIONS = 'auth.decision.v1'
    CHALLENGES = 'auth.challenge_required.v1'


def envelope_to_command(payload: dict) -> EvaluateLoginCommand:
    return EvaluateLoginCommand(user_id=payload['user_id'], ip=payload['ip'], device=payload['device'],
                                lat=payload['lat'], lon=payload['lon'], country=payload['country'], ts=payload['ts'],
                                success=payload.get('success'))


def risk_to_payload(user_id, decision, score, reasons): return {'user_id': user_id, 'decision': decision,
                                                                'score': score, 'reasons': reasons}


def risk_score_payload(user_id, score, reasons): return {'user_id': user_id, 'score': score, 'reasons': reasons}
