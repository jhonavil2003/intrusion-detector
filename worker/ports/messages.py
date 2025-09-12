from typing import Protocol, Any, Iterable


class Message:
    def __init__(self, body: Any, receipt: str | None = None, raw: Any = None):
        self.body = body
        self.receipt = receipt
        self.raw = raw


class QueueConsumer(Protocol):
    def receive(self, max_messages: int, wait_time_seconds: int, visibility_timeout: int) -> Iterable[Message]: ...

    def delete(self, receipt: str) -> None: ...