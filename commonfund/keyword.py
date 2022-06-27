# get pmids for papers using a DCC/project as a keyword
# Requires a csv with the following columns:
# DCC or Program Abbreviation, Full Name, Type, similar repository
import argparse
import csv
import json
import os
import sys

import requests

from commonfund import helper

# https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
def create_cli(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Path to csv of program names and abbreviations"
    )
    parser.add_argument(
        "--keyword-key",
        type=str,
        required=True,
        help="Path to csv containing the key",
        dest="key",
    )
    return parser.parse_args(arguments)


def build_esearch_url(short_name, long_name=None):
    end_portion = "+NOT+(Review[Publication Type])&retmax=100000&retmode=json"
    short_portion = f'("{short_name}"[Title/Abstract]+OR+"{short_name}"[Text Word]'
    if long_name:
        long_portion = f'+OR+"{long_name}"[Title/Abstract]+OR+"{long_name}"[Text Word])'
    else:
        long_portion = ")"
    return f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={short_portion}{long_portion}{end_portion}"


def parse_key(key_path):
    out = []
    with open(key_path, "r") as f:
        dict_reader = csv.DictReader(f)
        for row in dict_reader:
            row_fmt = {**row}
            row_fmt["Type"] = row_fmt.get("Type", "").lower().strip().replace(" ", "_")
            assert row_fmt["Type"] in [
                "cfde_dcc",
                "external",
            ], f"Incorrect key: {row_fmt['Type']}, must be cfde_dcc or external"
            out.append(row_fmt)
    return out


def make_call(entry):
    INITIAL_DELAY = 0.1
    out = {}
    short = entry.get("DCC or Program Abbreviation", None)
    long_name = entry.get("Full Name", None)
    item_type = entry.get("Type", None)
    out["competes_with"] = entry.get("Similar Repository")
    if not out["competes_with"]:
        out["competes_with"] = None
    out["type"] = entry.get("Type", None)
    out["program"] = short
    if short == long_name:
        long_name = None
    if short in [
        "MassIVE",
        "GEO",
        "SPARC",
        "ENCODE",
        "HERITAGE",
        "HMP",
    ]:
        print(f"[WARNING] Processing {long_name} instead of {short}")
        short = long_name
        long_name = None
    target_url = build_esearch_url(short, long_name)
    json_out = helper.safe_request_json(target_url, INITIAL_DELAY)
    if not json_out:
        out["pmid_list"] = []
        print(f"[WARNING] No entries returned for {entry}")
        return out
    pmid_list = json_out.get("esearchresult", {}).get("idlist", [])
    if not pmid_list:
        print(f"[WARNING] No entries returned for {entry}")
    out["pmid_list"] = pmid_list
    return out


# testing

# args = create_cli(["--keyword-key", "input/keyword-key.csv"])
# parsed = parse_key(args.key)
# output = make_call(parsed[0])

if __name__ == "__main__":
    output_json = []
    args = create_cli()
    parsed_key = parse_key(args.key)
    for entry in parsed_key:
        temp = make_call(entry)
        output_json.append(temp)
    helper.make_out_dirs()
    out_path = os.path.join("data", "intermediate", "keyword_results.json")
    with open(out_path, "w") as f:
        json.dump(output_json, f)
        print(f"[INFO] Writing file to {out_path}")


# MassIVE, HERITAGE, Exercise Transcriptome Meta-analysis
