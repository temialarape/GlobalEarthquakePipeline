import requests
import pandas as pd

# --- Configuration ---
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

USGS_PARAMS = {
    "format": "geojson",
    "starttime": "2026-01-01",   # adjust date range as needed
    "endtime": "2026-08-31",
    "minmagnitude": 4.5,          # adjust threshold as needed
    "orderby": "time"
}

OUTPUT_FILE = "earthquakes_usgs.csv"


def categorize_severity(magnitude):
    """Classify an earthquake's severity based on its magnitude."""
    if magnitude < 5.0:
        return "Minor"
    elif magnitude < 6.0:
        return "Moderate"
    elif magnitude < 7.0:
        return "Strong"
    else:
        return "Major"


def fetch_usgs():
    """Fetch earthquake data from USGS and flatten into a DataFrame."""
    response = requests.get(USGS_URL, params=USGS_PARAMS)
    response.raise_for_status()
    payload = response.json()

    rows = []
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
        rows.append({
            "id": feature.get("id"),
            "place": props.get("place"),
            "magnitude": props.get("mag"),
            "time_ms": props.get("time"),  # milliseconds since epoch
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2],
            "tsunami": props.get("tsunami"),
            "significance": props.get("sig"),
            "felt_reports": props.get("felt"),
            "alert": props.get("alert"),
            "type": props.get("type"),
            "url": props.get("url"),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["date"] = pd.to_datetime(df["time_ms"], unit="ms")
        df["severity_category"] = df["magnitude"].apply(categorize_severity)
        df["is_significant"] = df["significance"] > 500

    print(f"Fetched {len(df)} earthquake records")
    if not df.empty:
        print(df["severity_category"].value_counts())

    return df


if __name__ == "__main__":
    df = fetch_usgs()
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")