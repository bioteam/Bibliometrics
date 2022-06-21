import argparse
import json
import sys
import xml.etree.ElementTree as et

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select


def create_cli(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Path to JSON key for CFDE programs")
    parser.add_argument(
        "--cfde-key",
        type=str,
        required=True,
        help="Path to JSON file containing the CFDE program key",
        dest="cfde_key",
    )
    return parser.parse_args(arguments)


def parse_json_key(path):
    with open(path, "r") as f:
        data = json.load(f)
    out = {}
    for key in data.keys():
        values = data[key]
        out[values["abbrev"]] = values["url"]
    return out


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
    return program_data


def build_out(table, program):
    out = {}
    pmid_list = []
    out["competes_with"] = None
    out["type"] = "cfde_dcc"
    out["program"] = program
    for entry in table:
        cur = entry.get("PubMedID", "")
        pmid_list.append(cur)
    pmid_list = [i for i in pmid_list if i]
    out["pmid_list"] = pmid_list
    return out


def build_entry(key):
    args = create_cli(["--cfde-key", "input/cfde_programs_key.json"])
    prog_key = parse_json_key(args.cfde_key)
    opt = Options()
    opt.add_argument("-headless")
    driver = webdriver.Firefox(options=opt)
    driver.get(prog_key[key])
    select_all(driver)
    results_table = build_table(driver)
    driver.close()
    driver.quit()
    return build_out(results_table, key)


if __name__ == "__main__":
    args = create_cli()
    prog_key = parse_json_key(args.cfde_key)
    cfde_data = []
    new_name = "cfde_results.json"
    for key in prog_key.keys():
        try:
            entry = build_entry(key)
            cfde_data.append(entry)
            print(f"[INFO] n PMIDs for {key} is {len(entry['pmid_list'])}")
        except Exception as e:
            print(f"[ERROR] Problem with key {key}, exception is {e}")
            continue
    with open(new_name, "w") as f:
        json.dump(cfde_data, f)
        print(f"[INFO] Writing results to {new_name}")
