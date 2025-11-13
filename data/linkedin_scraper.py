import requests
from dotenv import load_dotenv
import os
import time


load_dotenv()

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")


def check_request_status(snapshot_id):
    url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    headers = {"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        print(response.json())
        return response.json()
    except Exception as e:
        print(f"Error checking request status: {e}")
        return None


def get_data(snapshot_id):
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"}
    params = {"format": "json"}

    try:
        response = requests.get(url, headers=headers, params=params)
        # print(response.json())
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def scrape_linkedin_by_profile_url(profile_url: str):
    url = "https://api.brightdata.com/datasets/v3/trigger"
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "dataset_id": "gd_lyy3tktm25m4avu764",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "profile_url",
    }
    data = [
        {
            "url": f"{profile_url}",
            "start_date": "2025-08-30T00:00:00.000Z",
            "end_date": "2025-11-03T00:00:00.000Z",
        },
    ]

    response = requests.post(url, headers=headers, params=params, json=data)
    response_json = response.json()
    id = response_json.get("snapshot_id")
    print(f"Snapshot ID: {id}")

    while True:
        time.sleep(10)
        status = check_request_status(id)
        if status.get("status") == "running":
            print("Request is still running...")
            continue
        elif status.get("status") == "ready":
            print("Request is ready!")
            break

    data = get_data(id)
    return data


if __name__ == "__main__":
    import json

    data = scrape_linkedin_by_profile_url("https://www.linkedin.com/in/s-ai-d")
    with open("data/said_post_data.json", "w") as f:
        json.dump(data, f, indent=4)
        f.close()
