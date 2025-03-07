import requests
import json

def ip_version(ip_addr):
    return "ipv4" if ip_addr == "A" or "." in ip_addr else "ipv6"

class AdguardHomeHost:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        
        self.session = requests.Session()
        self.session.auth = (username, password)
        
        self.sync_rewrite_list()

    def sync_rewrite_list(self):
        self.rewrite_list = self.get_rewrite_list()
    
    def get_rewrite_list(self):
        url = f"{self.hostname}/control/rewrite/list"
        r = self.session.get(url).json()
        
        res = {}
        for x in r:
            domain = x["domain"]
            addr = x["answer"]
            ipv = ip_version(addr)
            
            if domain not in res:
                res[domain] = {ipv: addr}
            else:
                res[domain][ipv] = addr
        
        return res
    
    def create_or_update_rewrite_rule(self, domain, target):
        ipv = ip_version(target)
        func = self.create_rewrite_rule if ipv not in self.rewrite_list.get(domain, {}) else self.update_rewrite_rule
        func(domain, target)
    
    def create_rewrite_rule(self, domain, target):
        url = f"{self.hostname}/control/rewrite/add"
        headers = {"content-type": "application/json"}
        data = {"domain": domain, "answer": target}
        self.session.post(url, data=json.dumps(data), headers=headers)
        self.sync_rewrite_list()
        
    def update_rewrite_rule(self, domain, target):
        url = f"{self.hostname}/control/rewrite/update"
        headers = {"content-type": "application/json"}
        ipv = ip_version(target)
        data = {
            "target": {"domain": domain, "answer": self.rewrite_list[domain][ipv]},
            "update": {"domain": domain, "answer": target},
        }
        self.session.put(url, data=json.dumps(data), headers=headers)