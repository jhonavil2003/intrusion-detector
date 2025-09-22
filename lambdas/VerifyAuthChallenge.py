def lambda_handler(event, _):
    import time
    exp = event['request']['privateChallengeParameters'].get('answer')
    ttl = int(event['request']['privateChallengeParameters'].get('ttl','0'))
    provided = event['request']['challengeAnswer']
    event['response']['answerCorrect'] = (provided == exp) and (int(time.time()) <= ttl)
    return event