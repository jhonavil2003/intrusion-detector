from .value_objects import RiskScore


class DecisionPolicy:
    def __init__(self, challenge_threshold=40.0, block_threshold=80.0):
        self.challenge_threshold = challenge_threshold
        self.block_threshold = block_threshold

    def decide(self, risk: RiskScore) -> str:
        if risk.value >= self.block_threshold: return "BLOCK"
        if risk.value >= self.challenge_threshold: return "CHALLENGE"
        return "ALLOW"
