from commonfund import openalex
from commonfund import icite
from commonfund import flagship

data = flagship.parse_csv("input/flagships.csv")
# target = flagship.elink_api(data[6])
target = flagship.elink_api(data[13])
target["source"] = "cites_a_flagship"
icite_res = icite.process_pmid_key_entry(target)
oa_out = []
for n, entry in enumerate(icite_res):
    try:
        temp = openalex.call_openalex(entry)
        parsed = openalex.parse_openalex(temp)
        oa_out.append({**entry, **parsed})
    except Exception as e:
        print(f"Problem with index {n}")
        continue


with open("data/final/flagship_icite_oa_results.json", "r") as f:
    complete_data = json.load(f)
