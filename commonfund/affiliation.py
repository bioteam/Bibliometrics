# Add the last author's affiliation and add it to a new json doc for the DCC
import json
import os
from pprint import pprint
import time
import requests


def read_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


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
    return res.json()


# test_file = read_json("data/Glycoscience.json")


def get_geo(address, polite):
    res = safe_request_json(address + polite)
    region = res.get("geo", {}).get("region", "")
    country = res.get("geo", {}).get("country_code")
    name_ = res.get("display_name")
    return region, country, name_


def backup_institute_info(author_address, polite):
    out = {}
    auth_data = safe_request_json(author_address + polite)
    last_institute_node = auth_data.get("last_known_institution", {})
    if not last_institute_node:
        out["institute_name"] = None
        out["institute_url"] = None
        out["geo_country"] = None
        out["geo_region"] = None
        return out
    last_institute_url = last_institute_node.get("id", "").replace(
        "https://", "https://api."
    )
    region, country, display_name = get_geo(last_institute_url, polite)
    out["institute_name"] = display_name
    out["institute_url"] = last_institute_url
    out["geo_country"] = country
    out["geo_region"] = region
    return out


def get_institute_info(institute_node, polite):
    out = {}
    institute_url = institute_node.get("id", "").replace("https://", "https://api.")
    if not institute_url:
        print("No institute url for {institute_node}")
        out["institute_name"] = None
        out["institute_url"] = None
        out["geo_country"] = None
        out["geo_region"] = None
        return out
    region, country, display_name = get_geo(institute_url, polite)
    out["institute_name"] = display_name
    out["institute_url"] = institute_url
    out["geo_country"] = country
    out["geo_region"] = region
    return out


# missing affil https://openalex.org/W4214951143
def openalex_authors(entry):
    """based on an `entry`, get the openalex authors data"""
    # new: last_author_openalex, last_author_raw_affil_string,
    # institute_name, institute_url, geo_region, geo_country
    time.sleep(0.2)  # respect rate limit
    error = None
    polite = "&mailto=nicholas@bioteam.net"
    out_entry = {**entry}
    oa_url = out_entry["openalex"].replace("https://", "https://api.")
    data = safe_request_json(oa_url + polite)
    # respect rate limit
    authors_list = data["authorships"]
    # NOTE HACK, ASSUMES ONE LAST AUTHOR
    try:
        last_author_node = [
            i for i in authors_list if i.get("author_position", "") == "last"
        ][-1]
    except IndexError as e:
        print(f"missing last author, taking first author for {out_entry['openalex']}")
        last_author_node = authors_list[0]
    author_openalex_url = (
        last_author_node.get("author", {}).get("id").replace("https://", "https://api.")
    )
    out_entry["last_author_openalex"] = author_openalex_url
    out_entry["last_author_raw_affil_string"] = last_author_node.get(
        "raw_affiliation_string"
    )
    affiliation_node_list = last_author_node.get("institutions", [])
    # NOTE HACK, ASSUMES LAST AFFIL IS OFFICIAL AFFIL
    try:
        institute_info = get_institute_info(affiliation_node_list[-1], polite)
    except IndexError as e:
        print(f"missing affiliation {out_entry['openalex']}")
        error = f"Author {author_openalex_url} missing affiliation node for {oa_url}"
        institute_info = backup_institute_info(author_openalex_url, polite)
    out_entry = {**out_entry, **institute_info}
    out_entry["author_error"] = error
    return out_entry


# entry = test_file[10]
# e2 = openalex_authors(entry)
# pprint(e2)


def add_geo(path):
    """give the path to a json doc, return"""
    data = read_json(path)
    new_path = path.replace(".json", "-GEO.json")
    out = []
    total = len(data)
    for n, entry in enumerate(data):
        print(f"[INFO] {n+1} out of {total}")
        try:
            new_entry = openalex_authors(entry)
        except Exception as e:
            print(f"[ERROR] Problem with entry: {entry}")
            print(f"[ERROR] Unhandled Exception: {e}")
            new_entry = {**entry}
            new_entry["institute_name"] = None
            new_entry["institute_url"] = None
            new_entry["geo_country"] = None
            new_entry["geo_region"] = None
            new_entry["last_author_openalex"] = None
            new_entry["last_author_raw_affil_string"] = None
            new_entry["author_error"] = f"Unhandled Exception: {e}"
        out.append(new_entry)
    return out, new_path


def write_data(path, data):
    if os.path.exists(path):
        print(f"[WARNING] File {path} already exists. Exiting")
        return
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    target_paths = [
        "data/Gabriella-Miller-Kids-First.json",
        "data/Glycoscience.json",
        "data/Molecular-Transducers-of-Physical-Activity-Clinical-Centers.json",
        "data/Human-Microbiome-Project.json",
        "data/ExRNA.json",
        "data/Metabolomics.json",
        "data/Stimulating-Peripheral-Activity-to-Relieve-Conditions-(SPARC).json",
        "data/Library-of-Integrated-Network-Based-Cellular-Signatures-(LINCS).json",
        "data/HuBMAP.json",
        "data/Genotype-Tissue-Expression-(GTEx).json",
        "data/4D-Nucleome.json",
    ]
    for path in target_paths:
        print(f"[INFO] Processing {path}...")
        geo, new_path = add_geo(path)
        write_data(new_path, geo)
        print(f"[INFO] Writing output to {new_path}")
    print("[INFO] Done")
