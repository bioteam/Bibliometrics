import os
import json
from pprint import pprint
import re
import time
import xml.etree.ElementTree as et

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select


def fmt_program_name(prog_name):
    return re.sub(pattern=r"\(\d+\)", repl="", string=prog_name).strip()


def get_prog_name(driver):
    name_xpath = "/html/body/div[1]/div/div[2]/div/div[3]/div/div/div/div/div/div/div/div[1]/b/span"
    name_str = driver.find_element(by="xpath", value=name_xpath).text
    return fmt_program_name(name_str)


def get_header(pub_table):
    thead = pub_table.find_element(by="tag name", value="thead")
    header_row = thead.find_element(by="tag name", value="tr")
    header_items = header_row.find_elements(by="tag name", value="th")
    return [col_name.text for col_name in header_items]


def get_table_row(header, table_row):
    data = {}
    tr_items = table_row.find_elements(by="tag name", value="td")
    assert len(tr_items) == len(header), "Mismatch lenght of table and length of row"
    for n, item in enumerate(tr_items):
        cur_header = header[n]
        data[cur_header] = item.text
    return data


def fmt_table(data_table, program_name):
    out = []
    for item in data_table:
        new_fmt = {
            "program": program_name,
            "publication_title": item["Publication Title"],
            "published_date": item["Publication Date"],
            "pmid": item["PubMedID"],
            "journal": item["Journal"],
        }
        out.append(new_fmt)
    return out


def select_all(driver):
    # select "All"
    show_all_select = Select(driver.find_element(by="tag name", value="select"))
    show_all_select.select_by_visible_text("All")


def build_table(driver):
    table_selection = driver.find_element(by="id", value="datatable-1")
    header = get_header(table_selection)
    tbody = table_selection.find_element(by="tag name", value="tbody")
    trows = tbody.find_elements(by="tag name", value="tr")
    program_data = []
    for trow in trows:
        row = get_table_row(header, trow)
        program_data.append(row)
    program_name = get_prog_name(driver)
    return fmt_table(program_data, program_name)


def pmid_to_doi(pmid):  # 34485947
    """Use pubmed api to parse and get DOI for next query"""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    efetch_res = requests.get(url)
    text = efetch_res.text
    try:
        etxml = et.fromstring(text)
    except Exception as e:
        print(f"[ERROR] ET parsing. Input is:\n{text}")
        raise e
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


def run(url):
    opt = Options()
    opt.add_argument("-headless")
    driver = webdriver.Firefox(options=opt)
    driver.get(url)
    select_all(driver)
    results_table = build_table(driver)
    # select and save the table download the table
    driver.close()
    driver.quit()
    fin_table = []
    for entry in results_table:
        print(f"[INFO] Processing PMID: {entry['pmid']}")
        try:
            new_entry = process_entry(entry)
            fin_table.append(new_entry)
        except Exception as e:
            print(f"[ERROR] Problem with entry: {entry}\n error is {e}")
            continue
        time.sleep(0.25)  # respect pubmed rate limit
    program = fin_table[0].get("program", "unknown")
    program = os.path.join("data", program.strip().replace(" ", "-") + ".json")
    return fin_table, program


if __name__ == "__main__":
    print("[INFO] Starting")
    TARGET_PROGRAMS = [
        "Genotype-Tissue Expression (GTEx)",  # September 2010
        "Human Microbiome Project",  # 2007 for part 1, then 2014 again
        "Library of Integrated Network-Based Cellular Signatures (LINCS)",  # 2010 pilot, now on 2014 phase. has a very nice publication filter https://lincsproject.org/LINCS/publications
        "Metabolomics",
        "ExRNA",
        "Glycoscience",
        "4D Nucleome",
        "Stimulating Peripheral Activity to Relieve Conditions (SPARC)",
        "Gabriella Miller Kids First",
        "Molecular Transducers of Physical Activity Clinical Centers",
        "HuBMAP",
    ]
    if not os.path.exists("data"):
        print("[INFO] Making data directory...")
        os.mkdir("data")
    with open("cfde_programs_key.json", "r") as f:
        keys = json.load(f)
    program_urls = []
    for prog in TARGET_PROGRAMS:
        program_urls.append(keys[prog])
    # NOTE! must download the geko driver and have it on your PATH https://github.com/mozilla/geckodriver/releases/tag/v0.31.0
    for n, url in enumerate(program_urls):
        print("\n######\n")
        print(f"[INFO] Processing URL: {url}. Number {n+1} of {len(program_urls)}")
        table, program = run(url)
        with open(program, "w") as f:
            json.dump(table, f, indent=2)
        print(f"[INFO] Writing to: {program}")
