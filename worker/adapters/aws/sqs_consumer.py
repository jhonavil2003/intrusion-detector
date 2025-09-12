import boto3
from ...ports.messages import Message, QueueConsumer


class SQSConsumer(QueueConsumer):
    def __init__(self, region: str, queue_url: str):
        self.queue_url = queue_url;
        self.client = boto3.client("sqs", region_name=region)

    def receive(self, max_messages: int, wait_time_seconds: int, visibility_timeout: int):
        resp = self.client.receive_message(
            QueueUrl=self.queue_url, MaxNumberOfMessages=max(1, min(max_messages, 10)),
            WaitTimeSeconds=wait_time_seconds, VisibilityTimeout=visibility_timeout,
            MessageAttributeNames=["All"]
        )
        for m in resp.get("Messages", []):
            yield Message(body=m.get("Body", "{}"), receipt=m["ReceiptHandle"], raw=m)

    def delete(self, receipt: str) -> None:
        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt)
