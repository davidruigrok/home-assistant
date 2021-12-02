import os
from dotenv import load_dotenv


load_dotenv()

CF_ACCESS_TOKEN = os.getenv("CF_ACCESS_TOKEN")
ZONE_ID = os.getenv("ZONE_ID")
HA_EXTERNAL_URL = os.getenv("HA_EXTERNAL_URL")
HA_INTERNAL_IP = os.getenv("HA_INTERNAL_IP")
HA_ACCESS_TOKEN = os.getenv("HA_ACCESS_TOKEN")
ADMIN_PHONE_ID = os.getenv("ADMIN_PHONE_ID")
PROJECT_NAME = os.getenv("PROJECT_NAME")
