import requests
import json
from datetime import datetime, timedelta, timezone

# === 🔑 API Key ===
API_KEY = "b5fb3cdd-d486-4dab-8df8-02ab44d5d5c1"
headers = {"Authorization": f"Key {API_KEY}"}

# === 🗺️ Probes grouped by cities (rozšířený seznam) ===
regions = {
    "Ceske_Budejovice": [795, 1009194, 1003512, 1003575, 1004776, 16701, 1000182, 29550, 23835, 1011064],
    "Liberec_Usti_n_Labem": [2126, 3263, 10647, 11149, 218, 20713, 24976, 1004840, 1004839, 839],
    "Prague": [1010268, 1004989, 1012986, 4062, 53238, 1010467, 7211, 1000267, 10222, 62712],
    "Karlovy_Vary_Plzen": [62300, 18433, 24120, 19301, 1010525, 65512, 20551, 50714, 1000221, 20127],
    "Pardubice": [33280, 29754, 1000093, 50535, 605, 61191, 1007202, 1000088, 32730, 1008559],
    "Brno": [21452, 1004850, 21646, 13494, 19228, 1000276, 25757, 23232, 25746, 1000032],
    "Ostrava": [1007563, 53824, 747, 1000197, 14341, 1000198, 1000035, 1000773, 20128, 1009198],
}

# === 🎯 Measurement targets ===
targets = ["seznam.cz", "nix.cz", "google.cz", "cesnet.cz"]

# === ⚙️ Parameters ===
packets = 3             
interval = 900           
duration_hours = 24       

# Začátek za 1 minutu, konec po 24h
start_time = int((datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp())
stop_time = int((datetime.now(timezone.utc) + timedelta(hours=duration_hours)).timestamp())

# === Flatten all probes ===
all_probes = [probe for region in regions.values() for probe in region]

# === Create measurements ===
for target in targets:
    measurement_data = {
        "definitions": [
            {
                "target": target,
                "description": f"FINAL PING to {target} every 15 min for 24h",
                "type": "ping",
                "af": 4,
                "packets": packets,
                "interval": interval,
                "spread": 60,
                "is_oneoff": False,
            }
        ],
        "probes": [
            {"requested": len(all_probes), "type": "probes", "value": ",".join(map(str, all_probes))}
        ],
        "start_time": start_time,
        "stop_time": stop_time,
    }

    create_url = "https://atlas.ripe.net/api/v2/measurements/"
    response = requests.post(create_url, headers=headers, json=measurement_data)
    measurement = response.json()

    if "measurements" in measurement:
        measurement_id = measurement["measurements"][0]
        print(f"✅ Measurement created → {target} (ID: {measurement_id})")
    else:
        print("❌ Error creating measurement:")
        print(json.dumps(measurement, indent=2))

