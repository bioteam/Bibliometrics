### parse and add icite keys
import argparse
import json
import sys

from commonfund import helper


def create_cli(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Path to JSON PMID ID source key")
    parser.add_argument(
        "--pmid-key",
        type=str,
        required=True,
        help="Path to JSON file containing the results",
        dest="pmid_key",
    )
    return parser.parse_args(arguments)


def batch_pmids(pmids):
    GROUP_SIZE = 75
    if not pmids:
        return []
    return [
        ",".join(pmids[n : n + GROUP_SIZE]) for n in range(0, len(pmids), GROUP_SIZE)
    ]


def _check_path(path):
    if path.startswith("keyword"):
        return "keyword_search"
    if path.startswith("cfde"):
        return "cfde_website"
    if path.startswith("flagship"):
        return "cites_a_flagship"
    else:
        raise (AssertionError(f"Cannot identify data source from {path}"))


def parse_result_file(path):
    source = _check_path(path)
    with open(path, "r") as f:
        data = json.load(f)
    for entry in data:
        entry["source"] = source
    return data


def call_icite_batch(pmid_batch):
    url = f"https://icite.od.nih.gov/api/pubs?pmids={pmid_batch}&fl=pmid,year,relative_citation_ratio,apt,nih_percentile,is_research_article,is_clinical"
    json_ret = helper.safe_request_json(url)
    return json_ret["data"]


def process_pmids(pmid_list):
    icite_res = []
    as_batched = batch_pmids(pmid_list)
    for batch in as_batched:
        icite_res += call_icite_batch(batch)
    return icite_res


def create_master_icite(icite_data):
    fmt_data = {}
    for item in icite_data:
        pmid = item.get("pmid", None)
        if not pmid:
            continue
        fmt_data[str(pmid)] = item
    return fmt_data


def process_pmid_key_entry(entry):
    entry_out = []
    entry_competes_with = entry.get("competes_with", None)
    entry_type = entry.get("type", None)
    entry_program = entry.get("program", None)
    entry_source = entry.get("source", None)
    entry_pmids = entry.get("pmid_list", [])
    if not entry_pmids:
        temp = {}
        temp["pmid"] = None
        temp["competes_with"] = entry_competes_with
        temp["type"] = entry_type
        temp["program"] = entry_program
        temp["source"] = entry_source
        temp["icite_rcr"] = None
        temp["icite_apt"] = None
        temp["icite_nih_percentile"] = None
        temp["icite_is_clinical"] = None
        temp["icite_is_research_article"] = None
        return [temp]
    pmid_info = create_master_icite(process_pmids(entry_pmids))
    for pmid_entry in entry_pmids:
        temp = {}
        try:
            target_icite_data = pmid_info.get(pmid_entry, {})
            temp["competes_with"] = entry_competes_with
            temp["pmid"] = pmid_entry
            temp["type"] = entry_type
            temp["program"] = entry_program
            temp["source"] = entry_source
            temp["icite_rcr"] = target_icite_data.get("relative_citation_ratio", None)
            temp["icite_apt"] = target_icite_data.get("apt", None)
            temp["icite_nih_percentile"] = target_icite_data.get("nih_percentile", None)
            temp["icite_is_clinical"] = target_icite_data.get("is_clinical", None)
            temp["icite_is_research_article"] = target_icite_data.get(
                "is_research_article", None
            )
            entry_out.append(temp)
        except Exception as e:
            print(f"[ERROR] Entry: {entry}, PMID: {pmid_entry}, exception: {e}")
            continue
    return entry_out


# testing

# args = create_cli(["--pmid-key", "keyword_results.json"])
# results_file = parse_result_file(args.pmid_key)
# icite_processed = []
# for current in results_file:
#     icite_processed += process_pmid_key_entry(current)


if __name__ == "__main__":
    args = create_cli()
    results_file = parse_result_file(args.pmid_key)
    icite_processed = []
    len_results = len(results_file)
    for n, current in enumerate(results_file):
        print(
            f"[INFO] Processing: {current.get('program','unknown')}, {n} of {len_results}"
        )
        icite_processed += process_pmid_key_entry(current)
    new_name = args.pmid_key.replace("_results.json", "_icite_results.json")
    with open(new_name, "w") as f:
        json.dump(icite_processed, f)
    print(f"[INFO] Wrote results to {new_name}")
