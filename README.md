# Code use

For each citation path, we have a file to generate a list of pubmed IDs and two other files to build the icite info and OpenAlex info based on these sources. Each python script focuses on a different set of APIs to generate the initial set of PMIDs, and the output of each is then processed by `icite.py` and `openalex.py`, using those respective API's to add the necessary keys. The results from `openalex.py` are then ready to be analyzed alone or in combination with the other sources. 

Each "source" has a separate program to generate the initial set of citations:
- `keyword.py` for the keyword search 
- `cfde.py` for scraping the CFDE citations page
- `flagship.py` for searching flagship paper citations

For example, if we want to generate the keywords dataset:

`keyword.py --keyword-key path-to-keyword-key.csv` Uses the `path-to-keyword-key.csv` to build a JSON file with a list of entries and PMIDs for each item

This program writes a JSON file with a list of DCC or competitors where each entry is:

```
[
    {"competes_with": null,
     "type": "cfde_dcc",
     "program": "HuBMAP",
     "pmid_list": [1232145, 1231245, ...]
     },
     // ...

]
```

The JSON is written to a file named `keyword_results.json`. The other programs will be named `cfde_results.json` or `flagship_results.json`.

The result files from this initial step are processed (separately) by the `icite.py`, which requires a path to that file, which will be prefixed by "keyword", "cfde", or "flagship".

The three input metadata files and flags for usage are:
- `python keyword.py --keyword-key input/keyword-key.csv` producing the keyword results `keyword_results.json`
- `python commonfund/flagship.py --flagship-key input/flagships.csv` producing the "papers citing flagships" results `flagship_results.json`
- `python commonfund/cfde.py --cfde-key input/cfde_programs_key.json` producing the CFDE citations page results `cfde_results.json`

## Adding iCite metadata

For adding iCite metadata to the keywords results:

`icite.py --pmid-key keyword_results.json`

This script takes each entry's list of PMIDs from `{keyword/cfde/flagship}_results.json`, and creates a new set of entries with the following keys, one for each publication:
- `competes_with`
- `type`
- `program`
- `source`
- `icite_rcr`
- `icite_apt`
- `icite_nih_percentile`
- `icite_is_clinical`
- `icite_is_research_article`

The results will look like the following:

```
[
    {
    "pmid": 1235325,
    "competes_with": null,
    "type": "cfde_dcc",
    "program": "LINCS",
    "source": "keyword_search",
    "icite_rcr": null,
    "icite_apt": 0.0,
    "icite_nih_percentile": null,
    "icite_is_clinical": "No",
    "icite_is_research_article": "Yes"
  },
  // ...

]
```


The file is written to `{keyword/cfde/flagship}_icite_results.json`, and can then be passed to OpenAlex.


## Openalex metadata
Note this is the slowest API since all requests must be done serially. The dataset at the end of this process is considered "final" and ready for analysis. 

`python openalex.py --icite-key keyword_icite_results.json` 


- `oa_author_name`
- `oa_institute_name`
- `oa_institute_url`
- `oa_geo_country`
- `oa_geo_city`
- `oa_geo_region`
- `oa_affil_string`
- `oa_openalex_id`
- `oa_publication_title`
- `oa_publication_date`
- `oa_publication_year`
- `oa_publisher_name`
- `oa_journal_name`
- `oa_total_citations`
- `oa_is_open_access`
- `oa_mesh`

`oa_mesh` is a list of objects where each object has the following keys:
- `oa_mesh_id`
- `oa_mesh_name`
- `oa_mesh_category`

The keys listed above are added to the keys from `icite.py`, creating the final dataset for each category. The results will look like the following:

```
[
  {
    "competes_with": null,
    "pmid": "35551182",
    "type": "cfde_dcc",
    "program": "4D Nucleome",
    "source": "cites_a_flagship",
    "icite_rcr": null,
    "icite_apt": 0.05,
    "icite_nih_percentile": null,
    "icite_is_clinical": "No",
    "icite_is_research_article": "Yes",
    "oa_publication_title": "Reconstruct high-resolution 3D genome structures for diverse cell-types using FLAMINGO",
    "oa_publication_year": 2022,
    "oa_publication_date": "2022-05-12",
    "oa_total_citations": 0,
    "oa_is_open_access": true,
    "oa_openalex_id": "https://api.openalex.org/W4280582334",
    "oa_publisher_name": "Springer Nature",
    "oa_journal_name": "Nature Communications",
    "oa_author_name": "Jianrong Wang",
    "oa_affil_string": "Department of Computational Mathematics, Science and Engineering, Michigan State University, East Lansing, MI, 48824, USA. wangj164@msu.edu.",
    "oa_institute_name": "Michigan State University",
    "oa_institute_url": "https://api.openalex.org/I87216513",
    "oa_geo_region": "Michigan",
    "oa_geo_country": "US",
    "oa_geo_city": "East Lansing"
    "oa_mesh": [
      {
        "oa_mesh_id": "D002843",
        "oa_mesh_name": "Chromatin",
        "oa_mesh_category": true
      },
      {
        "oa_mesh_id": "D002875",
        "oa_mesh_name": "Chromosomes",
        "oa_mesh_category": true
      },
      {
        "oa_mesh_id": "D002843",
        "oa_mesh_name": "Chromatin",
        "oa_mesh_category": false
      },
    // ...
    ],
  },
  // ...
]
```

The output file will be named `{keyword/cfde/flagship}_icite_oa_results.json`. 



## Reading the data with R and jsonlite

To read the data documents individually, use the following:

```{R}
# one file
keyword_dataset <- jsonlite::fromJSON(""keyword_icite_oa_results.json")
```

To read all files with the ending `*_icite_oa_results.json` in the directory into one data frame, use:

```
library(dplyr)
library(jsonlite)

data <- bind_rows(purrr::map(list.files(path=".", pattern="_icite_oa_results.json",full.names = T), fromJSON))

```
