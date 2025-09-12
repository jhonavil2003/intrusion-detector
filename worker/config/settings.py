from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    region: str;
    queue_url: str;
    profiles_path: str
    wait_time_seconds: int;
    visibility_timeout: int;
    max_number_of_messages: int
    publish_sns: bool;
    topic_risk_scores: str | None;
    topic_decisions: str | None;
    topic_challenges: str | None

    @staticmethod
    def from_env() -> "Settings":
        g = os.getenv
        return Settings(
            region=g("AWS_REGION") or g("AWS_DEFAULT_REGION") or "us-east-1",
            queue_url=g("AUTH_ATTEMPTS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/713843767123/auth-attempts-dlq"),
            profiles_path=g("PROFILES_PATH", "/data/profiles.json"),
            wait_time_seconds=int(g("WAIT_TIME_SECONDS", "20")),
            visibility_timeout=int(g("VISIBILITY_TIMEOUT", "60")),
            max_number_of_messages=int(g("MAX_NUMBER_OF_MESSAGES", "10")),
            publish_sns=(g("PUBLISH_SNS", "true").lower() == "true"),
            topic_risk_scores=g("RISK_SCORES_TOPIC_ARN"),
            topic_decisions=g("DECISIONS_TOPIC_ARN"),
            topic_challenges=g("CHALLENGES_TOPIC_ARN"),
        )
