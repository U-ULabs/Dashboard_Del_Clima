import sys
sys.path.insert(0, '/home/kali/project_export')

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("METEOBLUE_API_KEY")

LATITUDE = 6.2442
LONGITUDE = -75.5812
BASE_URL = "http://my.meteoblue.com/packages/basic-day"

params = {
    "apikey": API_KEY,
    "lat": LATITUDE,
    "lon": LONGITUDE,
    "asl": 1500,
    "tz": "America/Bogota",
    "format": "json"
}

response = requests.get(BASE_URL, params=params, timeout=10)
data = response.json()

print("Meteoblue API Response Keys:")
print(data.keys())
print("\ndata_day keys:")
if 'data_day' in data:
    print(data['data_day'].keys())
    print("\nFirst day sample:")
    for key in data['data_day'].keys():
        print(f"{key}: {data['data_day'][key][0] if data['data_day'][key] else 'N/A'}")
