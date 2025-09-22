import boto3
from ...ports.messages import Publisher


class SNSPublisher(Publisher):
    def __init__(self, region: str): self.client = boto3.client("sns", region_name=region)

    def publish(self, topic_arn: str, message: str) -> None: self.client.publish(TopicArn=topic_arn, Message=message)
