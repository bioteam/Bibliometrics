import csv
import json
import os

import requests


def read_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def safe_request_json(url):
    print(f"[INFO] Requesting URL: {url}")
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
        json_doc = res.json()
    except Exception as e:
        print(f"[WARNING] Requests parse json Exception is {e}")
        json_doc = None
    if not json_doc:
        print(
            f"[WARNING] Could not return JSON for {res.url}. Response is {res.response}"
        )
        return []
    return json_doc


def normalize_program(entity, source):
    """Take an entry from a directory and normalize the program name and add the source"""
    SOURCE_ENUM = ["cites_a_flagship", "keyword_search", "cfde_website"]
    assert source in SOURCE_ENUM, f"[ERROR] '{source}' must be one of {SOURCE_ENUM}"
    name_map = {
        "4D Nucleome": "4D Nucleome",
        "ExRNA": "ExRNA",
        "Gabriella Miller Kids First": "Kids First",
        "Genotype-Tissue Expression (GTEx)": "GTEx",
        "Glycoscience": "Glycoscience",
        "HuBMAP": "HuBMAP",
        "Human Microbiome Project": "HMP",
        "Library of Integrated Network-Based Cellular Signatures (LINCS)": "LINCS",
        "Metabolomics": "Metabolomics",
        "Molecular Transducers of Physical Activity Clinical Centers": "MoTrPAC",
        "Stimulating Peripheral Activity to Relieve Conditions (SPARC)": "SPARC",
    }
    out = {**entity}
    out["source"] = source
    orig_name = out.get("program", None)
    if not orig_name:
        print(f"[INFO] Cannot find program name for {entity}, returning original")
        return out
    normalized_name = name_map.get(orig_name, None)
    if not normalized_name:
        print(
            f"[INFO] Cannot program name in key for {orig_name}, returning original map"
        )
        return out
    out["program"] = normalized_name
    return out


def get_icite(entity):
    out = {**entity}
    pmid = entity.get("pmid", None)
    out["icite_rcr"] = None
    out["icite_apt"] = None
    out["icite_nih_percentile"] = None
    out["icite_is_clinical"] = None
    out["icite_is_research_article"] = None
    if not pmid:
        print(f"[ERROR] Cannot locate PMID for {entity}")
        return out
    url = f"https://icite.od.nih.gov/api/pubs?pmids={pmid}&fl=pmid,year,relative_citation_ratio,apt,nih_percentile,is_research_article,is_clinical"
    icite = safe_request_json(url)
    if not icite:
        return out
    data_0 = icite.get("data", [{}])[0]
    out["icite_rcr"] = data_0.get("relative_citation_ratio", None)
    out["icite_apt"] = data_0.get("apt", None)
    out["icite_nih_percentile"] = data_0.get("nih_percentile", None)
    out["icite_is_clinical"] = data_0.get("is_clinical", None)
    out["icite_is_research_article"] = data_0.get("is_research_article", None)
    return out


def format_entities(entity_list, source):
    master_list = []
    for entity in entity_list:
        try:
            cur = get_icite(normalize_program(entity, source))
        except Exception as e:
            err_str = f"[WARNING] Problem with {entity}, Exception {e}"
            print(err_str)
            continue
        master_list.append(cur)
    return master_list


def parse_flagship_key(flagship_key_path):
    with open(flagship_key_path, "r") as f:
        reader = csv.DictReader(f)
        out = []
        for row in reader:
            out.append(row)
        out_fmt = {}
        for item in out:
            pmid = item.get("PMID")
            out_fmt[pmid] = item
    return out_fmt


def add_similar_repository_flagship(entity_list, flagship_key):
    for entity in entity_list:
        entity["source"] = "cites_a_flagship"
        source_pmid = entity.get("flagship_pmid", {})
        try:
            flagship_source = flagship_key.get(source_pmid, None).get(
                "Competes with", None
            )
            if not flagship_source:
                flagship_source = None
            entity["similar_repository"] = flagship_source
        except Exception as e:
            entity["similar_repository"] = None
            continue
    return entity_list


def add_similar_repository(entity_list, similar_repository):
    for item in entity_list:
        item["similar_repository"] = similar_repository
    return entity_list


def gather_json(base_path):
    paths = [
        os.path.join(base_path, i) for i in os.listdir(base_path) if i.endswith(".json")
    ]
    out = []
    for path in paths:
        out += read_json(path)
    return out


def get_icite_batch(pmid_batch):
    url = f"https://icite.od.nih.gov/api/pubs?pmids={pmid_batch}&fl=pmid,year,relative_citation_ratio,apt,nih_percentile,is_research_article,is_clinical"
    icite = safe_request_json(url)
    return icite["data"]


def group_pmids(data, group_size=75):
    target_pmids = [i["pmid"] for i in data if i["pmid"]]
    grouped = [
        ",".join(target_pmids[n : n + group_size])
        for n in range(0, len(target_pmids), group_size)
    ]
    return grouped


def create_master_icite(icite_data):
    fmt_data = {}
    for item in icite_data:
        pmid = item.get("pmid", None)
        if not pmid:
            continue
        fmt_data[str(pmid)] = item
    return fmt_data


if __name__ == "__main__":
    #### Scraped Data
    print("[INFO] Processing Scraped data...")
    cfde_website = gather_json("data/scraped")
    master_cfde_website = format_entities(cfde_website, "cfde_website")
    master_cfde_website = add_similar_repository(master_cfde_website, None)
    with open("cfde_website_data.json", "r") as f:
        print("Writing Scraped data Master to cfde_website_data.json")
        json.dump(master_cfde_website, f, indent=2)

    #### Flagships
    print("[INFO] Processing Flagship data...")
    flagship_data = gather_json("data/flagship")
    flagship_key = parse_flagship_key("flagships.csv")
    flagship_data = add_similar_repository_flagship(flagship_data, flagship_key)
    pmids_grouped = group_pmids(flagship_data)
    all_icite_data = []
    for group in pmids_grouped:
        all_icite_data += get_icite_batch(group)
        master_icite = create_master_icite(all_icite_data)
    f_data = []
    for entry in flagship_data:
        temp_entry = {**entry}
        entry_pmid = entry.get("pmid", None)
        if not entry_pmid:
            continue
        icite_target = master_icite.get(entry_pmid, {})
        temp_entry["icite_rcr"] = icite_target.get("relative_citation_ratio", None)
        temp_entry["icite_apt"] = icite_target.get("apt", None)
        temp_entry["icite_nih_percentile"] = icite_target.get("nih_percentile", None)
        temp_entry["icite_is_clinical"] = icite_target.get("is_clinical", None)
        temp_entry["icite_is_research_article"] = icite_target.get(
            "is_research_article", None
        )
        f_data.append(temp_entry)
    with open("from_flagship.json", "w") as f:
        json.dump(f_data, f, indent=2)

    #### Keywords
    keyword_data = gather_json("data/keyword")
