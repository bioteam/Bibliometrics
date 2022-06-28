# https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/
import argparse
import csv
import json
import os
import sys


from commonfund import helper  # safe_request_json()


def create_cli(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Path to csv of flagship publications")
    parser.add_argument(
        "--flagship-key",
        type=str,
        required=True,
        help="Path to JSON file containing the results",
        dest="flagship_key",
    )
    return parser.parse_args(arguments)


def parse_csv(path):
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        out = []
        for row in reader:
            out.append(row)
    return out


def elink_api(entry):
    INITIAL_DELAY = 0.1
    out = {}
    flagship_pmid = entry.get("PMID", None)
    competes_with = entry.get("Competes with", "")
    fund_type = entry.get("Funding", "")
    fund_name = "unknown"
    dcc_name = entry.get("DCC/Repo", None)
    if fund_type == "CFDE":
        fund_name = "cfde_dcc"
    if fund_type == "External":
        fund_name = "external"
    if not fund_name in ["cfde_dcc", "external"]:
        err_str = (
            f"[WARNING] Prog type not known, funding was '{fund_type}' using 'unknown'"
        )
        print(err_str)
    if not competes_with:
        competes_with = None
    out["competes_with"] = competes_with
    out["type"] = fund_name
    out["program"] = dcc_name
    out["flagship_pmid"] = flagship_pmid
    if not flagship_pmid:
        out["pmid_list"] = []
        return out

    base = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id={flagship_pmid}&retmode=json"
    json_out = helper.safe_request_json(base, INITIAL_DELAY)
    if not json_out:
        json_out = {}
    linksets = json_out.get("linksets")
    try:
        pmid_list = (
            json_out.get("linksets", [{}])[0].get("linksetdbs", [{}])[0].get("links")
        )
        if not pmid_list:
            f"[WARNING] Problem getting PMIDs for {flagship_pmid}."
    except Exception as e:
        err_str = f"[WARNING] Problem getting PMIDs for {flagship_pmid}. Exception {e}"
        print(err_str)
        pmid_list = []
    out["pmid_list"] = pmid_list
    return out


# testing
# args = create_cli(["--flagship-key", "input/flagships.csv"])
# parsed_csv = parse_csv(args.flagship_key)
# new_name = "flagship_results.json"

if __name__ == "__main__":
    args = create_cli()
    parsed_csv = parse_csv(args.flagship_key)
    len_total = len(parsed_csv)
    new_name = "flagship_results.json"
    flagships_out = []
    for n, entry in enumerate(parsed_csv):
        print(f"[INFO] Processing {n} out of {len_total}")
        try:
            temp = elink_api(entry)
            flagships_out.append(temp)
        except Exception as e:
            err = f"Problem with index {n}, entry {entry}, Exception is {e}"
            print(err)
            continue
    helper.make_out_dirs()
    out_path = os.path.join("data", "intermediate", new_name)
    with open(out_path, "w") as f:
        json.dump(flagships_out, f)
        print(f"[INFO] Wrote results to {out_path}")
