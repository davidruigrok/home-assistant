# Source:
# https://www.cloudflare.com/ips
# https://support.cloudflare.com/hc/en-us/articles/200169166-How-do-I-whitelist-CloudFlare-s-IP-addresses-in$

for i in `curl https://www.cloudflare.com/ips-v4`; do iptables -I INPUT -p tcp -m multiport --dports 8123 -s$
for i in `curl https://www.cloudflare.com/ips-v6`; do ip6tables -I INPUT -p tcp -m multiport --dports 8123 -$


if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi

# Add internal IP addresses
iptables -I INPUT -p tcp -m multiport --dports 8123 -s $HA_INTERNAL_IP/24 -j ACCEPT
iptables -I INPUT -p tcp -m multiport --dports 8123 -s $DOCKER_IP_RANGE -j ACCEPT

# Avoid racking up billing/attacks
# WARNING: If you get attacked and CloudFlare drops you, your site(s) will be unreachable.
#iptables -A INPUT -p tcp -m multiport --dports http,https -j DROP
iptables -A INPUT -p tcp -m multiport --dports 8123 -j DROP
ip6tables -A INPUT -p tcp -m multiport --dports 8123 -j DROP