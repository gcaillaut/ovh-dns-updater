from tqdm import tqdm
import ovh
import requests
import yaml

def get_ip():
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    return ip

def get_dynhosts(client, zone):
    dynhost_ids = client.get(f"/domain/zone/{zone}/dynHost/record")
    dynhosts = [client.get(f"/domain/zone/{zone}/dynHost/record/{id}") for id in dynhost_ids]
    return dynhosts

def get_statichosts(client, zone):
    host_ids_a = client.get(f"/domain/zone/{zone}/record", fieldType="A")
    host_ids_aaaa = client.get(f"/domain/zone/{zone}/record", fieldType="AAAA")
    return {
        "ipv4": [client.get(f"/domain/zone/{zone}/record/{rid}") for rid in host_ids_a],
        "ipv6": [client.get(f"/domain/zone/{zone}/record/{rid}") for rid in host_ids_aaaa],
    }

def get_hosts_to_remove(target: set, current: set):
    return current - target

def get_hosts_to_create(target: set, current: set):
    return target - current

def get_hosts_to_update(target: set, current: set):
    return target.intersection(current)

def update_dynhosts(cfg, client, zone, ip):
    dynhosts = get_dynhosts(client, zone)
    current_subdomains = {x["subDomain"] for x in dynhosts}
    target_subdomains = set(cfg["dynhosts"][zone]["subdomains"])
    
    if cfg["dynhosts"][zone].get("remove_others", False):
        subdomain2id = {x["subDomain"]: x["id"] for x in dynhosts}
        for subdomain in get_hosts_to_remove(target_subdomains, current_subdomains):
            record_id = subdomain2id[subdomain]
            client.delete(f"/domain/zone/{zone}/dynHost/record/{record_id}")
        
    for subdomain in get_hosts_to_create(target_subdomains, current_subdomains):
        client.post(f"/domain/zone/{zone}/dynHost/record", ip=ip, subDomain=subdomain)
        
def update_statichosts(cfg, client, zone):
    hosts = get_statichosts(client, zone)
    current_subdomains = {
        ipv: {x["subDomain"] for x in hosts[ipv]}
        for ipv in ("ipv4", "ipv6")
    }
    subdomain2id = {
        ipv: {x["subDomain"]: x["id"] for x in hosts[ipv]}
        for ipv in ("ipv4", "ipv6")
    }
    
    for x in cfg["statichosts"][zone]:
        ttl = x.get("ttl", 0)
        subdomains = set(x["subdomains"])
        for ipv, field_type in (("ipv4", "A"), ("ipv6", "AAAA")):
            if ip := x.get(ipv, None):
                record_create = get_hosts_to_create(subdomains, current_subdomains[ipv])
                record_update = get_hosts_to_update(subdomains, current_subdomains[ipv])
                for d in record_create:
                    client.post(f"/domain/zone/{zone}/record", fieldType=field_type, subDomain=d, target=ip, ttl=ttl)
                for d in record_update:
                    rid = subdomain2id[ipv][d]
                    client.put(f"/domain/zone/{zone}/record/{rid}", subDomain=d, target=ip, ttl=ttl)

def main(cfg):
    client = ovh.Client()
    ip = get_ip()
    print(f"IP address is {ip}")
    for zone in tqdm(cfg["dynhosts"], desc="Updating dynamic hosts"):
        update_dynhosts(cfg, client, zone, ip)
        
    for zone in tqdm(cfg["statichosts"], desc="Updating static hosts"):
        update_statichosts(cfg, client, zone)
    

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="settings/config.yaml")
    
    args = parser.parse_args()
    
    with open(args.config, "rt", encoding="utf-8") as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    main(cfg)
