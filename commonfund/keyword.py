# get pmids for papers using a DCC/project as a keyword
from pprint import pprint
import requests

# openalex cites flagship
# openalex keyword

PMID_4DN = "28905911"
clin = "23456789"
# step 1, get DOI and cited papers from iCite


def icite_api(pmid):
    url = f"https://icite.od.nih.gov/api/pubs?pmids={pmid}&fl=pmid,year,citation_count,cited_by,cited_by_clin,doi,title"
    req = requests.get(url)
    print(f"Requesting url: '{req.url}'")
    return req.json()


def parse_icite(icite_ret):
    """create field for DOI, create openalex search url and add all pmids to one list."""
    assert (
        len(icite_ret["data"]) == 1
    ), f"Only one pmid at a time is supported. Data is: {pprint(icite_ret)}"
    data = icite_ret["data"][0]
    out = {**data}
    print(out["cited_by_clin"])
    if out["cited_by_clin"] != None:
        out["cited_by"] = out["cited_by"] + out["cited_by_clin"]
        print("[INFO] Clinical citations")
    del out["cited_by_clin"]
    out["citation_count"] = len(out["cited_by"])
    out["openalex"] = "https://api.openalex.ord/works/https://doi.org/" + out["doi"]
    return out


flag4dn = parse_icite(icite_api(PMID_4DN))
