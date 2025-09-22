import os, time, json, boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

events = boto3.client("events")
lmb    = boto3.client("lambda")
lmb = boto3.client("lambda", region_name="us-east-1")

EVENT_BUS   = os.getenv("EVENT_BUS_NAME","default")
DETAIL_TYPE = os.getenv("DETAIL_TYPE","auth.attempts.v1")
RISK_FN     = os.getenv("RISK_LAMBDA_ARN")          # ARN o nombre de RiskDecision
FALLBACK    = os.getenv("ON_ERROR_DECISION","CHALLENGE")  # ALLOW | CHALLENGE | BLOCK

def put_attempt(detail):
    events.put_events(Entries=[{
        "Source": "intrusion-detector.cognito",
        "DetailType": DETAIL_TYPE,
        "Detail": json.dumps(detail),
        "EventBusName": EVENT_BUS
    }])

def invoke_risk(payload):
    print("Invoke Function")
    print("Funcion Name", RISK_FN)
    resp = lmb.invoke(FunctionName=RISK_FN, InvocationType="RequestResponse",
                      Payload=json.dumps(payload).encode("utf-8"), Qualifier='$LATEST',)
    if resp.get("FunctionError"):
        # logs del callee (opcional): base64 en LogResult si pediste LogType="Tail"
        print("Callee logs:", resp.get("LogResult"))
        raise RuntimeError(f"Invoke error: {resp['FunctionError']}")
    body = resp.get("Payload").read()
    print("risk", body)
    return json.loads(body or "{}")

def lambda_handler(event, _ctx):
    logger.info("This is an informational log message.")
    print("This will also appear in CloudWatch Logs.")
    md = event.get('request', {}).get('clientMetadata') or {}
    attrs = event.get('request', {}).get('userAttributes') or {}
    username = event.get('userName')
    print("user", username)
    payload = {
        "user_id": username,
        "ip": md.get('ip'),
        "device": md.get('deviceId','unknown'),
        "lat": float(md.get('lat') or 0.0),
        "lon": float(md.get('lon') or 0.0),
        "country": md.get('country') or attrs.get('custom:country') or 'NA',
        "ts": time.time()
    }
    print("payload", payload)

    # 1) Telemetría (no bloquear si falla)
    try: put_attempt(payload)
    except Exception: pass

    request = event.get("request", {})
    # Asegura que 'response' exista aunque no venga en el evento
    response = event.setdefault("response", {})
    session = request.get("session", []) or []

    if len(session) == 1 and session[0].get("challengeName") == "SRP_A":
        response["issueTokens"] = False
        response["failAuthentication"] = False
        response["challengeName"] = "PASSWORD_VERIFIER"

    elif (
        len(session) == 2
        and session[1].get("challengeName") == "PASSWORD_VERIFIER"
        and session[1].get("challengeResult") is True
    ):
        try:
            risk = invoke_risk(payload)  # {"decision","score","reasons"}
            decision = str(risk.get("decision","ALLOW"))
            score    = float(risk.get("score", 0))
            reasons  = risk.get("reasons", [])
        except Exception:
            print("Error en RiskDecision")
            decision = FALLBACK
            score = -1; reasons = ["RISK_SERVICE_ERROR"]

        if decision == "BLOCK":
            response["issueTokens"] = False
            response["failAuthentication"] = True

        if decision == "CHALLENGE":    
            response['challengeName'] = 'CUSTOM_CHALLENGE'
            response['issueTokens'] = False
            response['failAuthentication'] = False

        if decision == "ALLOW": 
            response["issueTokens"] = True
            response["failAuthentication"] = False

    elif (
        len(session) == 3
        and session[2].get("challengeName") == "CUSTOM_CHALLENGE"
        and session[2].get("challengeResult") is True
    ):
        response["issueTokens"] = True
        response["failAuthentication"] = False
        response["challengeName"] = "CUSTOM_CHALLENGE"

    elif (
        len(session) == 4
        and session[3].get("challengeName") == "CUSTOM_CHALLENGE"
        and session[3].get("challengeResult") is True
    ):
        response["issueTokens"] = True
        response["failAuthentication"] = False

    else:
        response["issueTokens"] = False
        response["failAuthentication"] = True

    return event
