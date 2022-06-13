# get citations from flagship publications
import argparse
import csv
import json
import os
import sys
import time


import requests


def safe_request_json(url):
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


def parse_csv(path):
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        out = []
        for row in reader:
            out.append(row)
    return out


def parse_cited_by_entry(program, pmid, entry):
    openalex = entry.get("id", "")
    title = entry.get("title", "")
    pmid_parsed = (
        entry.get("ids", {})
        .get("pmid", "")
        .replace("https://pubmed.ncbi.nlm.nih.gov/", "")
    )
    published_date = entry.get("publication_date", "")
    publication_year = entry.get("publication_year", None)
    journal = entry.get("host_venue", {}).get("display_name", "")
    total_citations = entry.get("cited_by_count", 0)
    is_open_access = entry.get("open_access", {}).get("is_oa", None)
    return {
        "flagship_pmid": pmid,
        "program": program,
        "pmid": pmid_parsed,
        "openalex": openalex,
        "publication_title": title,
        "published_date": published_date,
        "publication_year": publication_year,
        "journal": journal,
        "total_citations": total_citations,
        "is_open_access": is_open_access,
    }


# journal, total_citations, is_open_access
def open_alex_flagship(entry):
    pmid = entry.get("PMID", None)
    if not pmid:
        return []
    URL = f"https://api.openalex.org/works/pmid:{pmid}"
    flagship_program = entry.get("DCC/Repo")
    res_json = safe_request_json(URL)
    if not res_json:
        return []
    cited_by_url = res_json.get("cited_by_api_url")
    cited_by_json = safe_request_json(cited_by_url + "&per-page=200")
    total = cited_by_json.get("meta", {}).get("count", 0)
    if total == 0:
        return []
    cited_list = cited_by_json.get("results")
    page = 1
    while total > len(cited_list):
        page += 1
        url = f"{cited_by_url}&per-page=200&page={page}&mailto=nicholas@bioteam.net"
        print(f"[INFO] Fetching URL:\n {url}")
        cur_res = safe_request_json(url).get("results")
        cited_list += cur_res

    cited_data = []
    for entry in cited_list:
        cited_data.append(parse_cited_by_entry(flagship_program, pmid, entry))
    return cited_data


def write_out(entry, out):
    n = 1
    f_string = f"flagship-{entry.get('DCC/Repo')}-{n}.json"
    out_path = os.path.join("data", f_string)
    while os.path.exists(out_path):
        n += 1
        f_string = f"flagship-{entry.get('DCC/Repo')}-{n}.json"
        out_path = os.path.join("data", f_string)
    print(f"[INFO] Writing to path: {out_path}")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Path to CSV Key")
    parser.add_argument("--key", help="path to flagship key")
    args = parser.parse_args()
    if not os.path.exists(args.key):
        print("[ERROR] Please pass a valid path")
        sys.exit()
    csv_key = parse_csv(args.key)
    for entry in csv_key:
        print(f"Processing {entry['DCC/Repo']} PMID {entry['PMID']}")
        out = open_alex_flagship(entry)
        if not out:
            continue
        write_out(entry, out)
