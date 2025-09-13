import json
from ...application.use_case import EvaluateLoginAttempt
from ...domain.services import RiskEngine, NewDeviceRule, UnusualHourRule, ImpossibleTravelRule, NewCountryRule, \
    FailedAttemptsRule, BadIPRule, ASNChangeRule
from ...domain.policies import DecisionPolicy
from ...infrastructure.repositories import FileUserProfileRepository, MemoryEventRepository
from ...infrastructure.geoip import GeoService
from ...infrastructure.ip_reputation import IPReputation
from ...infrastructure.context import Context
from ...infrastructure.mapping import envelope_to_command, risk_to_payload, risk_score_payload

class WorkerFactory:
    @staticmethod
    def build_use_case(store_path: str) -> EvaluateLoginAttempt:
        profiles = FileUserProfileRepository(store_path)
        events = MemoryEventRepository()
        engine = RiskEngine([NewDeviceRule(30), UnusualHourRule(20), ImpossibleTravelRule(40, 900), NewCountryRule(25),
                             FailedAttemptsRule(10, 3), BadIPRule(35), ASNChangeRule(15)])
        policy = DecisionPolicy(40, 80)
        ctx = Context(geo=GeoService(), iprep=IPReputation())
        return EvaluateLoginAttempt(profiles, events, engine, policy, ctx)

class Processor:
    def __init__(self, usecase: EvaluateLoginAttempt, publisher=None, topics: dict | None = None):
        self.usecase = usecase
        self.publisher = publisher
        self.topics = topics or {}

    def handle(self, payload: dict) -> dict:
        cmd = envelope_to_command(payload)
        decision, score, reasons = self.usecase.handle(cmd)
        result = {"user_id": cmd.user_id, "decision": decision, "score": score, "reasons": reasons}
        if self.publisher:
            if t := self.topics.get("risk"): self.publisher.publish(t, json.dumps(
                risk_score_payload(cmd.user_id, score, reasons)))
            if t := self.topics.get("decision"): self.publisher.publish(t, json.dumps(
                risk_to_payload(cmd.user_id, decision, score, reasons)))
            if decision in ("BLOCK", "CHALLENGE") and (t := self.topics.get("challenge")): self.publisher.publish(t,
                                                                                                                  json.dumps(
                                                                                                                      {
                                                                                                                          "user_id": cmd.user_id,
                                                                                                                          "reason": decision}))
        return result