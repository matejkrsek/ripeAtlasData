import requests
import csv
from datetime import datetime

# === 🔑 API Key ===
API_KEY = "b5fb3cdd-d486-4dab-8df8-02ab44d5d5c1"
headers = {"Authorization": f"Key {API_KEY}"}

# === 🗺️ Mapping of probes to cities (3 sondy / region) ===
regions = {
   "Ceske_Budejovice": [795, 1009194, 1003512, 1003575, 1004776, 16701, 1000182, 29550, 23835, 1011064],
    "Liberec_Usti_n_Labem": [2126, 3263, 10647, 11149, 218, 20713, 24976, 1004840, 1004839, 839],
    "Prague": [1010268, 1004989, 1012986, 4062, 53238, 1010467, 7211, 1000267, 10222, 62712],
    "Karlovy_Vary_Plzen": [62300, 18433, 24120, 19301, 1010525, 65512, 20551, 50714, 1000221, 20127],
    "Pardubice": [33280, 29754, 1000093, 50535, 605, 61191, 1007202, 1000088, 32730, 1008559],
    "Brno": [21452, 1004850, 21646, 13494, 19228, 1000276, 25757, 23232, 25746, 1000032],
    "Ostrava": [1007563, 53824, 747, 1000197, 14341, 1000198, 1000035, 1000773, 20128, 1009198],
}

# === 🔢 Measurement IDs (doplň později) ===
measurement_ids = {
    "seznam.cz": 133374801,
    "nix.cz": 133374805,
    "google.cz": 133374810,
    "cesnet.cz": 133374811,
}

# === 📁 Output file ===
output_file = "results_trace_final_test.csv"

# === 🧭 Helper: find city by probe ID ===
def find_city_by_probe(probe_id):
    for city, probes in regions.items():
        if probe_id in probes:
            return city
    return "Unknown_city"

# === 📥 Download and save results ===
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp_utc",
        "city",
        "probe_id",
        "target",
        "num_hops",
        "hop_ips",
        "hop_rtts"
    ])

    for target, mid in measurement_ids.items():
        if not mid:
            print(f"⚠️ Skipping {target} (no measurement ID assigned).")
            continue

        print(f"📥 Downloading traceroute results for {target} (ID: {mid})...")
        results_url = f"https://atlas.ripe.net/api/v2/measurements/{mid}/results/"
        response = requests.get(results_url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Error fetching results for {target}: {response.status_code}")
            continue

        results = response.json()
        if not isinstance(results, list) or len(results) == 0:
            print(f"⚠️ No results found for {target}.")
            continue

        for r in results:
            prb_id = r.get("prb_id")
            ts = r.get("timestamp")
            ts_readable = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""

            city = find_city_by_probe(prb_id)
            hops = r.get("result", [])

            hop_ips = []
            hop_rtts = []

            for hop in hops:
                if "result" in hop:
                    hop_ips.append([res.get("from") for res in hop["result"] if "from" in res])
                    hop_rtts.append([res.get("rtt") for res in hop["result"] if "rtt" in res])
                else:
                    hop_ips.append([])
                    hop_rtts.append([])

            num_hops = len(hops)

            writer.writerow([
                ts_readable,
                city,
                prb_id,
                target,
                num_hops,
                hop_ips,
                hop_rtts
            ])

