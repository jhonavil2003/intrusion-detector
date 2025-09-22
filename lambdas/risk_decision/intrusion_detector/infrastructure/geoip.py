from math import radians, sin, cos, sqrt, atan2
from ..domain.value_objects import GeoPoint


class GeoService:
    def distance_km(self, a: GeoPoint, b: GeoPoint) -> float:
        R = 6371.0
        dlat = radians(b.lat - a.lat)
        dlon = radians(b.lon - a.lon)
        lat1 = radians(a.lat)
        lat2 = radians(b.lat)
        h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * R * atan2(sqrt(h), sqrt(1 - h))
