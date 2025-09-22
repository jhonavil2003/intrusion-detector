# risk_decision.py
import os, json, time
import logging
logging.info(f"root: {os.listdir('/var/task')}")

from intrusion_detector.application.commands import EvaluateLoginCommand
from intrusion_detector.application.use_case import EvaluateLoginAttempt
from intrusion_detector.domain.services import (RiskEngine, NewDeviceRule, UnusualHourRule,
                                                ImpossibleTravelRule, NewCountryRule, FailedAttemptsRule, BadIPRule, ASNChangeRule)
from intrusion_detector.domain.policies import DecisionPolicy
from intrusion_detector.infrastructure.context import Context
from intrusion_detector.infrastructure.geoip import GeoService
from intrusion_detector.infrastructure.ip_reputation import IPReputation

# --- Repositorio de perfiles ---
USE_DDB = os.getenv("USE_DDB","false").lower()=="true"

from intrusion_detector.infrastructure.repositories import FileUserProfileRepository as ProfileRepo

CHALLENGE_T = float(os.getenv("CHALLENGE_THRESHOLD","40"))
BLOCK_T     = float(os.getenv("BLOCK_THRESHOLD","80"))

engine = RiskEngine([
    NewDeviceRule(30), UnusualHourRule(20), ImpossibleTravelRule(40,900),
    NewCountryRule(25), FailedAttemptsRule(10,3), BadIPRule(35), ASNChangeRule(15)
])
policy = DecisionPolicy(CHALLENGE_T, BLOCK_T)
ctx    = Context(geo=GeoService(), iprep=IPReputation())
repo   = ProfileRepo(os.getenv("PROFILES_PATH","/tmp/profiles.json"))

def lambda_handler(event, _):
    # espera: {"user_id","ip","device","lat","lon","country","ts"}
    cmd = EvaluateLoginCommand(
        user_id = event["user_id"],
        ip      = event.get("ip","0.0.0.0"),
        device  = event.get("device","unknown"),
        lat     = float(event.get("lat") or 0.0),
        lon     = float(event.get("lon") or 0.0),
        country = event.get("country","NA"),
        ts      = float(event.get("ts") or time.time()),
        success = None
    )
    uc = EvaluateLoginAttempt(repo, None, engine, policy, ctx)
    decision, score, reasons = uc.handle(cmd)
    return {"decision": decision, "score": score, "reasons": reasons}
