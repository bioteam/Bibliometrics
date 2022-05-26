from pprint import pprint
import json
import re
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


if __name__ == "__main__":

    URL = "https://commonfund.nih.gov/publications?pid=38"  #
    # NOTE! must download the geko driver and have it on your PATH https://github.com/mozilla/geckodriver/releases/tag/v0.31.0
    opt = Options()
    opt.add_argument("-headless")
    driver = webdriver.Firefox(options=opt)
    driver.get(URL)
    results_table = build_table(driver)
    # select and save the table download the table
    driver.close()
    driver.quit()

    print("[INFO] Table Data:")
    pprint(results_table)
    program = results_table[0].get("program", "unknown")
    program = program.strip().replace(" ", "-") + ".json"
    with open(program, "w") as f:
        json.dump(results_table, f, indent=2)
    print(f"[INFO] Table has {len(table_data)} publications.")
    print(f"[INFO] Writing to: {program}")
