import requests
import json

def ip_version(ip_addr):
    return "ipv4" if ip_addr == "A" or "." in ip_addr else "ipv6"

class AdguardHomeHost:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        
        self.session = requests.Session()
        self.session.auth = (username, password)
        
        self.rewrite_list = {}
        self.sync_rewrite_list()
        
    def add_to_rewrite_list(self, domain, target):
        ipv = ip_version(target)
        if domain not in self.rewrite_list:
            self.rewrite_list[domain] = {ipv: target}
        else:
            self.rewrite_list[domain][ipv] = target

    def sync_rewrite_list(self):
        url = f"{self.hostname}/control/rewrite/list"
        r = self.session.get(url).json()
        self.rewrite_list = {}
        for x in r:
            domain = x["domain"]
            target = x["answer"]
            self.add_to_rewrite_list(domain, target)
                
    def create_or_update_rewrite_rule(self, domain, target):
        ipv = ip_version(target)
        func = self.create_rewrite_rule if ipv not in self.rewrite_list.get(domain, {}) else self.update_rewrite_rule
        func(domain, target)
    
    def create_rewrite_rule(self, domain, target):
        url = f"{self.hostname}/control/rewrite/add"
        headers = {"content-type": "application/json"}
        data = {"domain": domain, "answer": target}
        self.session.post(url, data=json.dumps(data), headers=headers)
        self.add_to_rewrite_list(domain, target)
        
    def update_rewrite_rule(self, domain, target):
        url = f"{self.hostname}/control/rewrite/update"
        headers = {"content-type": "application/json"}
        ipv = ip_version(target)
        data = {
            "target": {"domain": domain, "answer": self.rewrite_list[domain][ipv]},
            "update": {"domain": domain, "answer": target},
        }
        
        if data["target"]["answer"] != data["update"]["answer"]:
            self.session.put(url, data=json.dumps(data), headers=headers)
            self.add_to_rewrite_list(domain, target)