from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluateLoginCommand:
    user_id: str
    ip: str
    device: str
    lat: float
    lon: float
    country: str
    ts: float
    success: bool | None = None
