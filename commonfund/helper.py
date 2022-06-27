import os
import requests
import time


def make_out_dirs():
    intermediate = os.path.join("data", "intermediate")
    final = os.path.join("data", "final")
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists(intermediate):
        os.mkdir(intermediate)
    if not os.path.exists(final):
        os.mkdir(final)
    return


def safe_request_json(url, initial_delay=None):
    if initial_delay:
        time.sleep(initial_delay)  # respect pubmed rate limit
    try:
        res = requests.get(url, timeout=5)
    except requests.exceptions.SSLError:
        print(f"[ERROR] OpenSSL Error for url {url}")
        return []
    if res.ok:
        return res.json()
    # wait if rate limited
    if res.status_code == 404:
        print(f"[ERROR] URL {res.url} not found!")
        return []
    print(
        f"Apparent rate limit for url {url}. Code: {res.status_code}. waiting 2 second then retry..."
    )
    time.sleep(2)
    try:
        res = requests.get(url, timeout=5)
    except requests.exceptions.SSLError:
        print(f"[ERROR] OpenSSL Error for url {url}")
        return []
    try:
        res.json()
    except Exception as e:
        print(f"[ERROR] Exception is {e}")
        print(f"[ERROR] bad JSON returned from {res.url}")
    return []
