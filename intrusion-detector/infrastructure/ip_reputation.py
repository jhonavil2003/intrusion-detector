class IPReputation:
    def __init__(self):
        self.bad_ips = {'185.220.101.1', '104.244.72.115'}
        self.ip_to_asn = {'200.25.0.1': 'AS19429', '200.25.0.2': 'AS19429', '8.8.8.8': 'AS15169',
                          '185.220.101.1': 'AS208294', '104.244.72.115': 'AS14061'}
        self.profile_asn = {}

    def is_bad(self, ip: str) -> bool: return ip in self.bad_ips

    def asn(self, ip: str): return self.ip_to_asn.get(ip)

    def asn_for_profile(self, profile): return self.profile_asn.get(profile.user_id)
