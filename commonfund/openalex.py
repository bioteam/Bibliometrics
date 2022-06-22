import argparse
import json
import sys

from commonfund import helper

POLITE = "&mailto=nicholas@bioteam.net"


def create_cli(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Path to iCite.py output key")
    parser.add_argument(
        "--icite-key",
        type=str,
        required=True,
        help="Path to JSON file containing the key",
        dest="icite_key",
    )
    return parser.parse_args(arguments)


def parse_icite_results(path):
    assert path.endswith(
        "_icite_results.json"
    ), f"Script requires output from icite.py. You passed {path}"
    with open(path, "r") as f:
        data = json.load(f)
    return data


def parse_oa_mesh(mesh_portion):
    out = []
    if not mesh_portion:
        return out
    for mesh in mesh_portion:
        temp = {}
        temp["oa_mesh_id"] = mesh.get("descriptor_ui", None)
        temp["oa_mesh_name"] = mesh.get("descriptor_name", None)
        temp["oa_mesh_category"] = mesh.get("is_major_topic", None)
        out.append(temp)
    return out


def get_institution_info(institution_list):
    out = {}
    if not institution_list:
        return out
    if len(institution_list) == 1:
        target = institution_list[0]
    else:
        target = institution_list[-1]
    # :'( I know. I just don't have time to properly fix it :'(
    try:
        out["oa_id"] = target.get("id", "").replace("https://", "https://api.")
    except AttributeError as e:
        out["oa_id"] = ""
    if out["oa_id"]:
        response_institute = helper.safe_request_json(out["oa_id"] + POLITE)
    else:
        response_institute = {}
    try:
        out["region"] = response_institute.get("geo", {}).get("region")
    except AttributeError as e:
        out["region"] = None
    try:
        out["country"] = response_institute.get("geo", {}).get("country_code")
    except AttributeError as e:
        out["country"] = None
    try:
        out["name"] = response_institute.get("display_name", None)
    except AttributeError as e:
        out["name"] = None
    try:
        out["city"] = response_institute.get("geo", {}).get("city")
    except AttributeError as e:
        out["city"] = None
    return out


def parse_authorship(authorship_portion):
    out = {}
    author_dict = {}
    if not authorship_portion:
        return out
    if len(authorship_portion) == 1:
        author_target = authorship_portion[0]
        author_dict["name"] = author_target.get("author", {}).get("display_name", None)
        author_dict["inst"] = author_target.get("institutions", [])
        author_dict["affil"] = author_target.get("raw_affiliation_string", None)
    else:
        for author in authorship_portion:
            if author.get("author_position") == "last":
                author_dict["name"] = author.get("author", {}).get("display_name", None)
                author_dict["inst"] = author.get("institutions", [])
                author_dict["affil"] = author.get("raw_affiliation_string", None)

    institute_dict = get_institution_info(author_dict.get("inst", []))
    out["oa_author_name"] = author_dict.get("name", None)
    out["oa_affil_string"] = author_dict.get("affil", None)
    out["oa_institute_name"] = institute_dict.get("name", None)
    out["oa_institute_url"] = institute_dict.get("oa_id", None)
    out["oa_geo_region"] = institute_dict.get("region", None)
    out["oa_geo_country"] = institute_dict.get("country", None)
    out["oa_geo_city"] = institute_dict.get("city", None)
    return out


def parse_openalex(response):
    if not response:
        response = {}
    oa_values = {}
    oa_values["oa_publication_title"] = response.get("display_name", None)
    oa_values["oa_publication_year"] = response.get("publication_year", None)
    oa_values["oa_publication_date"] = response.get("publication_date", None)
    oa_values["oa_total_citations"] = response.get("cited_by_count", None)
    oa_values["oa_is_open_access"] = response.get("host_venue", {}).get("is_oa", None)
    oa_values["oa_openalex_id"] = response.get("id", "").replace(
        "https://", "https://api."
    )
    oa_values["oa_publisher_name"] = response.get("host_venue", {}).get("publisher")
    oa_values["oa_journal_name"] = response.get("host_venue", {}).get("display_name")
    mesh_portion = response.get("mesh")
    author_portion = response.get("authorships", [])
    authors_parsed = parse_authorship(author_portion)
    oa_values["oa_mesh"] = parse_oa_mesh(mesh_portion)
    return {**oa_values, **authors_parsed}


def call_openalex(entry):
    pmid = entry.get("pmid")
    if not pmid:
        print("[WARNING] No PMID found")
        return {}
    url = f"https://api.openalex.org/works/pmid:{pmid}{POLITE}"
    openalex_response = helper.safe_request_json(url)
    if not openalex_response:
        print(f"[WARNING] No OA response, returning None for {entry}")
        return {}
    return openalex_response


# testing
# args = create_cli(["--icite-key", "keyword_icite_results.json"])
# data = parse_icite_results(args.icite_key)
# an_entry = call_openalex(data[11])
# parsed = parse_openalex(an_entry)


if __name__ == "__main__":
    args = create_cli()
    data = parse_icite_results(args.icite_key)
    total_len = len(data)
    oa_data = []
    for n, entry in enumerate(data):
        print(f"Processing {n} of {total_len} entries")
        try:
            oa_call = call_openalex(entry)
            parsed = parse_openalex(oa_call)
            oa_data.append({**entry, **parsed})
        except Exception as e:
            exception_string = (
                f"[WARNING] Problem with {entry}, index {n}, Exception is {e}"
            )
            print(exception_string)
            with open("oa_errors.json", "a") as f:
                f.write(exception_string)
            continue
    out_path = args.icite_key.replace("_results.json", "_oa_results.json")
    with open(out_path, "w") as f:
        json.dump(oa_data, f)
    print(f"[INFO] Wrote results to {out_path}")
