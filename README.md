# OVH DNS Updater

This script update your OVH's DNS zone. It supports IPv4 DynHosts and IPv4/IPv6 static hosts.

## How to use

You need to create an application key before using this script. More details [here](https://community.ovhcloud.com/community/fr/gestion-application-et-acces-api?id=community_question&sys_id=e750b14485de06d01e111c5c94ac5bc0)

You also need to create a consumer key using the provided script.

```
uv run print_consumer_key.py
```

Then rename (or copy) the file `ovh.conf.template` to `ovh.conf` and fill it with your keys.

An example configuration is provided in `settings/example.yaml`. Customize it according to your needs then run

```
uv run main.py --config settings/your-config.yaml
```