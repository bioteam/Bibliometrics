import json
import xml.etree.ElementTree as et

import requests


def pmid_to_doi(pmid):
    """Use pubmed api to parse and get DOI for next query"""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    efetch_res = requests.get(url)
    text = efetch_res.text
    etxml = et.fromstring(text)
    articleids = etxml.findall("./PubmedArticle/PubmedData/ArticleIdList/ArticleId")
    doi_raw = ""
    for a_id in articleids:
        if a_id.attrib["IdType"] == "doi":
            doi_raw = a_id.text
    return "https://doi.org/" + doi_raw


def openalex(doi):
    url = f"https://api.openalex.org/works/{doi}"
    res = requests.get(url)
    as_json = res.json()
    api_citations = (
        as_json["cited_by_api_url"] + "&group_by=publication_year&sort=key:desc"
    )
    # quit if no citations
    if as_json["cited_by_count"] == 0:
        as_json["citation_counts_by_year"] = []
        return as_json
    citations = requests.get(api_citations).json()
    gb = citations["group_by"]
    gb_out = []
    for item in gb:
        parsed = int(item["key"])
        gb_out.append({parsed: item["count"]})
    as_json["citation_counts_by_year"] = gb_out
    return as_json


def process_entry(entry):
    doi = pmid_to_doi(entry["pmid"])
    oa_res = openalex(doi)
    entry["openalex"] = oa_res["id"]
    entry["total_citations"] = oa_res["cited_by_count"]
    entry["published_date"] = oa_res["publication_date"]
    entry["publication_year"] = oa_res["publication_year"]
    entry["is_open_access"] = oa_res["open_access"]["is_oa"]
    entry["citation_counts_by_year"] = oa_res["citation_counts_by_year"]
    return entry


with open("4D-Nucleome.json", "r") as f:
    data = json.load(f)

entry = data[0]
out = process_entry(entry)
