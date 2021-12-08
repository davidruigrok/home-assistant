import requests
from env import (
    CF_ACCESS_TOKEN,
    ZONE_ID,
    HA_EXTERNAL_URL,
    HA_INTERNAL_IP,
    HA_ACCESS_TOKEN,
    ADMIN_PHONE_ID,
    PROJECT_NAME,
)
from bootstrap import logging
from urllib3.exceptions import InsecureRequestWarning


def get_current_ip_address() -> str:
    """
    Get current 'remote' ip address of Home Assistant
    :return:
    """

    res = requests.get('https://checkip.amazonaws.com/')
    if res.status_code == 200:
        return str(res.text.strip())


def get_cloudflare_ip_address() -> tuple:
    """
    Get current Home Assistant dns A record ip address
    :return:
    """
    resp = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/",
        headers={
            "Authorization": f"Bearer {CF_ACCESS_TOKEN}",
        },
    )

    if resp.status_code == 200:
        records = resp.json()["result"]
        for record in records:
            if record["name"] == HA_EXTERNAL_URL and record["type"] == "A":
                return record["id"], record["content"]


def send_notification(current_ip_address):
    """
    Send push notification about DNS update
    :param current_ip_address:
    :return:
    """
    url = f"https://{HA_INTERNAL_IP}:8123/api/services/notify/{ADMIN_PHONE_ID}"
    headers = {
        "Authorization": f"Bearer {HA_ACCESS_TOKEN}",
        "content-type": "application/json",
    }
    data = {
        "title": f"{HA_EXTERNAL_URL} DNS changed",
        "message": f"The DNS 'A' record for {HA_EXTERNAL_URL} has been changed to {current_ip_address}",
    }

    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    response = requests.post(url, headers=headers, json=data, verify=False)
    if response.status_code == 200:
        logging.info(
            f"{PROJECT_NAME}.messenger.status=SNT,"
            f"{PROJECT_NAME}.messenger.to={ADMIN_PHONE_ID},"
            f"{PROJECT_NAME}.messenger.service=notify"
        )
    else:
        logging.warning(
            f"{PROJECT_NAME}.messenger.status=NOSNT,"
            f"{PROJECT_NAME}.messenger.to={ADMIN_PHONE_ID},"
            f"{PROJECT_NAME}.messenger.service=notify"
        )


def auto_update_cloudflare_dns():
    """
    Verify and update Home Assistant A DNS records when changed
    :return:
    """
    # Let retrieve current cloudflare DNS A record IP address
    cloudflare_ip_address = get_cloudflare_ip_address()
    # Get current 'remote' IP address which should be used for Home Assistant
    current_ip_address = get_current_ip_address()
    if current_ip_address:
        # Compare both addresses
        if cloudflare_ip_address[1] != current_ip_address:
            logging.info(
                f"{PROJECT_NAME}.dns.status=CHG,{PROJECT_NAME}.dns.ip='{cloudflare_ip_address[1]}',"
                f"{PROJECT_NAME}.external.ip='{current_ip_address}'"
            )

            # External IP address of project changed, let's update it
            resp = requests.put(
                f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{cloudflare_ip_address[0]}",
                json={
                    "type": "A",
                    "name": HA_EXTERNAL_URL,
                    "content": current_ip_address,
                    "proxied": True,
                },
                headers={
                    "Authorization": f"Bearer {CF_ACCESS_TOKEN}",
                },
            )

            if resp.status_code == 200:
                logging.info(
                    f"Updated DNS A for {HA_EXTERNAL_URL} on cloudflare to {current_ip_address}"
                )
                # Let's send a push notification with update about the change
                send_notification(current_ip_address)

        else:
            logging.info(
                f"{PROJECT_NAME}.dns.status=NOCHG,{PROJECT_NAME}.dns.ip='{cloudflare_ip_address[1]}',"
                f"{PROJECT_NAME}.external.ip='{current_ip_address}'"
            )


logging.info(
    f"{PROJECT_NAME}.service=dns,{PROJECT_NAME}.service.func=auto_update_cloudflare_dns"
)
auto_update_cloudflare_dns()
