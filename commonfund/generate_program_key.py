import json
import re
from selenium import webdriver


def fmt_program_name(prog_name):
    return re.sub(pattern=r"\(\d+\)", repl="", string=prog_name).strip()


def get_program_key(driver):
    """There are a max of 43 PID's, navigate to each to build the list of URL's with program names"""
    name_xpath = "/html/body/div[1]/div/div[2]/div/div[3]/div/div/div/div/div/div/div/div[1]/b/span"
    base = "https://commonfund.nih.gov/publications?pid="
    out = {}
    for pid in range(1, 44):
        prog_url = f"https://commonfund.nih.gov/publications?pid={pid}"
        driver.get(prog_url)
        try:
            name_str = driver.find_element(by="xpath", value=name_xpath).text
            prog_name = fmt_program_name(name_str)
            out[prog_name] = prog_url
        except Exception as e:
            print(f"[WARNING] Couldn't find program name for url '{prog_url}'")
            continue
    return out


if __name__ == "__main__":
    driver = webdriver.Firefox()
    prog_key = get_all_program_names(driver)
    with open("cfde_programs_key.json", "w") as out:
        json.dump(prog_key, out, indent=2)
    print(
        f"[INFO] Saved program key to: '{os.path.join(os.getcwd(), 'cfde_programs.json')}'"
    )
