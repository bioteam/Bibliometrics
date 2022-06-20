import requests
import time


def safe_request_json(url, initial_delay=None):
    if initial_delay:
        time.sleep(initial_delay)  # problem with pubmed rate limits
    res = requests.get(url)
    if res.ok:
        return res.json()
    # wait if rate limited
    print(
        f"Apparent rate limit for url {url}. Code: {res.status_code}. waiting 2 second then retry..."
    )
    time.sleep(2)
    res = requests.get(url)
    try:
        res.json()
    except Exception as e:
        print(f"[ERROR] Exception is {e}")
        print(f"[ERROR] bad JSON returned from {res.url}")
    return []
