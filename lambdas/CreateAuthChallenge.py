import os
import time
import secrets
import logging
import boto3

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.getLogger().setLevel(LOG_LEVEL)
sns = boto3.client("sns")

OTP_TTL_SECONDS = int(os.getenv('OTP_TTL_SECONDS','180'))
SMS_SENDER_ID = os.getenv("SMS_SENDER_ID", "MediSupply")

def _send_code_sms(phone_number: str, code: str):
    msg = f"Tu código es {code}. Vence en {OTP_TTL_SECONDS // 60} min."
    attrs = {
        "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"}
    }

    if SMS_SENDER_ID:
        attrs["AWS.SNS.SMS.SenderID"] = {"DataType": "String", "StringValue": SMS_SENDER_ID}

    resp = sns.publish(
        PhoneNumber=phone_number,  
        Message=msg,
        MessageAttributes=attrs
    )
    logging.info({"published": True, "messageId": resp.get("MessageId")})

def lambda_handler(event, _):
    import time, random, os
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if event['request']['challengeName'] != 'CUSTOM_CHALLENGE':
        return event

    req = event.get("request", {}) or {}
    res = event.setdefault("response", {})
    attrs = req.get("userAttributes", {}) or {}

    phone = attrs.get("phone_number")
    
    code = f"{random.randint(0,999999):06d}"
    print(f"OTP: {code}")
    
    ttl = int(time.time()) + OTP_TTL_SECONDS
    event['response']['privateChallengeParameters'] = {'answer': code, 'ttl': str(ttl)}
    event['response']['publicChallengeParameters']  = {'delivery': 'SMS', 'length': '6'}

    try:
        _send_code_sms(phone, code)
    except Exception as e:
        logging.exception({"error": str(e)})
    
    return event