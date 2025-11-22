import requests
import os
import time

from dotenv import load_dotenv

load_dotenv()

AIML_API_KEY = os.getenv("AIML_API_KEY")
base_url = "https://api.aimlapi.com/v2"


def main():
    url = f"{base_url}/video/generations"
    payload = {
        "model": "alibaba/wan2.2-14b-animate-replace",
        "prompt": "Replace the man in the video",
        "video_url": "https://drive.google.com/uc?export=download&id=1boSqd2R6S44cTKBaGVSnq6qFyrjTU_4x",
        "image_url": "https://drive.google.com/uc?export=download&id=1fEZI8reegklCCrZyqcUVYcdyZWs50LOM",
        "resolution": "720p",
    }
    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Generation:", response.json())
    return response.json()


def get_video(gen_id):
    url = f"{base_url}/video/generations"
    params = {
        "generation_id": gen_id,
    }

    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()


if __name__ == "__main__":
    r = main()
    time.sleep(30)
    status = "generating"
    while status == "generating":
        video_response = get_video(r["id"])
        if video_response["status"] == "generating":
            time.sleep(10)
        else:
            break

    print(video_response)

    # print(
    #     get_video(
    #         "d610780a-b350-4863-9619-bfead29e0398:alibaba/wan2.2-14b-animate-replace"
    #     )
    # )
