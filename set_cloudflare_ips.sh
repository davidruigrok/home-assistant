#!/bin/bash

# Source:
# https://www.cloudflare.com/ips
# https://support.cloudflare.com/hc/en-us/articles/200169166-How-do-I-whitelist-CloudFlare-s-IP-addresses-in$

for i in `curl https://www.cloudflare.com/ips-v4`; do iptables -I INPUT -p tcp -m multiport --dports 8123 -s $i -j ACCEPT; done
for i in `curl https://www.cloudflare.com/ips-v6`; do ip6tables -I INPUT -p tcp -m multiport --dports 8123 -s $i -j ACCEPT; done

if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi

# Add internal IP addresses
iptables -I INPUT -p tcp -m multiport --dports 8123 -s $LOCAL_IP_RANGE -j ACCEPT
iptables -I INPUT -p tcp -m multiport --dports 8123 -s $DOCKER_IP_RANGE -j ACCEPT

# Make sure no other IP addresses can access your Home Assistant setup
# If you get attacked and CloudFlare drops you, your site(s) will be unreachable.
iptables -A INPUT -p tcp -m multiport --dports 8123 -j DROP
ip6tables -A INPUT -p tcp -m multiport --dports 8123 -j DROP
