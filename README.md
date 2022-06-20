# Code use

For each citation path, we have a file to generate a list of pubmed IDs and two other files to build the icite info and OpenAlex info based on these

Each "source" has a separate program to generate the initial set of citatoins:
- `keyword.py` for the keyword search 
- `cfde_citation.py` for scraping the CFDE citations page
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

The result files are processed (separately) by the `icite.py`, which requires a path to that file, which will be prefixed by "keyword", "cfde", or "flagship".

## Adding iCite metadata

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


## TODO openalex metadata

`openalex.py --icite-output keyword_icite_results.json` 

Each program focuses on a different set of APIs to generate the initial set of PMIDs, which are then processed by `icite.py` and `openalex.py`. The results from `openalex.py` are then ready to be analyzed alone or in combination with the other sources. 



## Reading the data with R and jsonlite

To read the data documents individually, use the following:

```{R}
# one file
full_dataset <- jsonlite::fromJSON()
```

To read all files with the ending *-GEO.json in the data directory into one data frame, use:

```
library(dplyr)
library(ggplot2)
library(jsonlite)
theme_set(theme_bw())

data <- bind_rows(purrr::map(list.files(path="data", pattern="-GEO.json",full.names = T), fromJSON))

```


# CFDE Bibliometrics Exploration


The CFDE DCCs are tasked with creating FAIR datasets that will be used by the scientific community. One method of assessing the "value" of a dataset is by measuring the number of times that dataset or DCC has been cited in the literature compared to similar non-CFDE funded datasets or repositories. 
Here, we explored the citations of CFDE DCC datasets over time, identifying highly cited DCCs and compared them to "similar" dataset repositories to paint a better picture of where CFDE DCC datasets stand in relation to others in the field. 

## DCC Flagship Publications

CFDE DCCs typically provide instructions for data use, including a "Flagship Publication" that researchers are instructed to cite in any publications resulting from use of their data. For example, The 4D Nucleome project provides [data use guidelines](https://data.4dnucleome.org/) on the portal home page requesting researchers cite [*The 4D nucleome project*](https://www.nature.com/articles/nature23884). We consider these publications "Flagship Publications", because they introduce the DCCs goals, data types, and philosophies, but do not typically contain original research material. We use Flagship Publications as a primary guide to track citations of a particular DCC. Table 1 lists the Flagship Publications we identified for the CFDE DCCs[^flagship_note]( **NOTE IN PROGRESS**).


| DCC                  | Flagship Publication Title                                                                                       | PMID     | Year Published | Direct Citations |
|----------------------|------------------------------------------------------------------------------------------------------------------|----------|----------------|------------------|
| 4D Nucleome          | The 4D nucleome project                                                                                          | 28905911 | 2017           | 195              |
| Glycoscience         | GlyGen: Computational and Informatics Resources for Glycoscience.                                                | 31616925 | 2019           | 37               |
| GTEx                 | The GTEx Consortium atlas of genetic regulatory effects across human tissues                                     | 32913098 | 2020           | 417              |
| HuBMAP               | The human body at cellular resolution: the NIH Human Biomolecular Atlas Program                                  | 31597973 | 2019           | 88               |
| SPARC                | The SPARC DRC: Building a Resource for the Autonomic Nervous System Community                                    | 34248680 | 2021           | 2                |
| IDG[^idg]            | Pharos: Collating protein information to shed light on the druggable genome                                      | 27903890 | 2017           | 99               |
| IDG[^idg]            | TCRD and Pharos 2021: mining the human proteome for disease biology                                              | 33156327 | 2021           | 12               |
| LINCS[^LINCS]        | The Library of Integrated Network-Based Cellular Signatures NIH Program...                                       | 29199020 | 2018           | 139              |
| LINCS[^LINCS]        | LINCS Data Portal 2.0: next generation access point for perturbation-response signatures                         | 31701147 | 2020           | 41               |
| MoTrPAC              | Molecular Transducers of Physical Activity Consortium (MoTrPAC): Mapping the Dynamic Responses to Exercise       | 32589957 | 2020           | 35               |
| Metabolomics[^metab] | Metabolomics Workbench: An international repository for metabolomics data and metadata, metabolite standards,... | 26467476 | 2016           | 186              |
| HMP                  |                                                                                                                  |          |                |                  |
| ExRNA                |                                                                                                                  |          |                |                  |
| Kids First           |                                                                                                                  |          |                |                  |


[^metab]: MORE PHASES, in progress
[^idg]: Note we could not identify a single flagship paper associated with IDG. Instead, we have used the *Pharos* publication, since it is the primary resource described on the [CFDE IDG page](https://commonfund.nih.gov/IDG), and the original *Pharos* Publication from 2017. We have listed a number of additional publications for IDG in the [Supplemental Materials Datasheet](https://docs.google.com/spreadsheets/d/1zmx-wxmOgWTC2lrmaDXcZ-KN6R2MdCzq8udqFgPWfAA/edit#gid=552619060).

[^LINCS]: Multiple flagship options are possible, associated with both the pilot phase and the current phase of LINCS. Other options include: [Koleti et al. 2018](https://pubmed.ncbi.nlm.nih.gov/29140462/), [Stathias et al. 2018](https://pubmed.ncbi.nlm.nih.gov/29917015/), [Vempati et al. 2014](https://pubmed.ncbi.nlm.nih.gov/24518066/), and [Duan et al. 2014](https://pubmed.ncbi.nlm.nih.gov/24906883/). 

[^flagship_note]: In some cases, we identified multiple Flagship Publications for DCCs (e.g. LINCS), and in others we could not identify a Flagship Publication based on our definition (e.g. IDG). In those cases, we used the closest approximations to a flagship publication (listed in Table 1, also see footnotes for individual entries). 


Tracking data DCC data usage via publications citing the Flagship Publication can provide an overview of data use, some flagship publications have only recently been published, while the datasets created by the consortium may have existed for significantly longer (e.g. Metabolomics **NICK PROVIDE CITATIONS FOR BOTH ROUNDS**). Additionally, some DCC datasets can be cited directly via DOI, for example in [SPARC](https://sparc.science/about/sparc-portal/6nqPLAgegexTuRSPsDi5nL/#publications-and-citations). Clicking the "Publications" link on the SPARC page provides a link to a PubMed search for [publications citing grants associated with SPARC](https://pubmed.ncbi.nlm.nih.gov/?term=(OD023873[gr])+OR+(OD023857[gr])+OR+(OD026580[gr])+OR+(OD025308[gr])+OR+(OD026545[gr])+OR+(TR002205[gr])+OR+(OD023854[gr])+OR+(OD025349[gr])+OR+(OD023848[gr])+OR+(OD025348[gr])+OR+(OD023850[gr])+OR+(NS113868[gr])+OR+(OD028183[gr])+OR+(OD023864[gr])+OR+(NS113873[gr])+OR+(OD028203[gr])+OR+(OD023872[gr])+OR+(OD023852[gr])+OR+(OD028191[gr])+OR+(OD024907[gr])+OR+(OD023847[gr])+OR+(DK116320[gr])+OR+(OD028201[gr])+OR+(OD026539[gr])+OR+(OD026577[gr])+OR+(OD023859[gr])+OR+(OD024899[gr])+OR+(OD025297[gr])+OR+(OD025307[gr])+OR+(TR002208[gr])+OR+(OD028190[gr])+OR+(OD024909[gr])+OR+(OD025306[gr])+OR+(DK116317[gr])+OR+(OD024898[gr])+OR+(OD023861[gr])+OR+(OD023871[gr])+OR+(DK116312[gr])+OR+(OD024912[gr])+OR+(OD025340[gr])+OR+(NS113869[gr])+OR+(OD026585[gr])+OR+(OD023860[gr])+OR+(OD025342[gr])+OR+(DK116311[gr])+OR+(OD026582[gr])+OR+(OD023867[gr])+OR+(OD023853[gr])+OR+(OD025347[gr])+OR+(OD024908[gr])+OR+(NS113871[gr])+OR+(NS113867[gr])+OR+(EB021716[gr])+OR+(EB021760[gr])+OR+(EB021780[gr])+OR+(EB021799[gr])+OR+(TR001925[gr])+OR+(18017[gr])+OR+(EB021787[gr])+OR+(EB021792[gr])+OR+(EB021759[gr])+OR+(EB021772[gr])+OR+(EB021793[gr])+OR+(TR001926[gr])+OR+(EB021790[gr])+OR+(TR001920[gr])+OR+(EB021877[gr])+OR+(OD023849[gr])+OR+(EB021789[gr])&sort=), revealing more publications that may have been missed by a cursory search by the flagship publications listed in Table 1. 

The CFDE website also provides an automatically updated list of [publications for each DCC](https://commonfund.nih.gov/publications?pid=0), updated monthly.

To address these challenges and remain consistent, we wrote code to automate gathering and condensing citation data from the following sources:
- All publications for each DCC listed on the [CFDE Publication Search Page](https://commonfund.nih.gov/publications?pid=0)
- All publications citing a Flagship Publication, where Flagship Publications are listed in Table 1. 
- All publications resulting from a keyword search of the DCC name in PubMed, filtering for journal articles.

We performed all keyword searches using the `[Text Word]` filter (e.g. `LINCS[Text Word]`), and the appropriate MeSH terms to select only "journal articles". For example the search term for LINCS: `(LINCS[Text Word]) AND (journal article[Publication Type])`.

Data was then processed to remove duplicate citations within a DCC (e.g. if a publication cited both the Flagship Publication and used the DCC name in the text, it would only be counted once), and analyzed the citation data in the following sections. 

## Building the Primary Citation Dataset

All searches and data processing steps are written as Python and R scripts that can be re-run at will to update the citation dataset used in this section. Citation results will change as time goes on, and this analysis can be re-run periodically to obtain updated results. 

To build the full dataset and re-run the analysis, run:

**TODO** Add script run instructions. Create Docker container to run all analysis in a reproducible manner. Can set up periodic updates on cloud if they want to keep the analysis as a dashboard. 

# TODO Section on primary citations

Describe the citation frequency over time of the DCCs. Normalize time so DCCs of different ages are compared based on a T0 (founding of the DCC?)

# TODO Section describing methods for comparing DCCS

Outside of CFDE, there are various repositories hosting similar datasets. We have identified repositories similar to the CFDE DCCs for the purpose of comparison... (in progress)


# TODO AI Ready Datasets

Which CFDE repository is most AI ready (comparing to similar repos and others)?

An interviewee at Metabolomics Workbench questoined whether their data was more AI/ML ready when compared to datasets from competing repositories. To address this question, we searched for papers AI/ML papers published using data from [Metabolomics Workbench](https://pubmed.ncbi.nlm.nih.gov/26467476) and the similar repositories: 
- [MassIVE](https://massive.ucsd.edu/ProteoSAFe/static/massive.jsp)
  - [Assembling the Community-Scale Discoverable Human Proteome](https://pubmed.ncbi.nlm.nih.gov/30172843/) (Flagship Publication)
- [MetaboLights](http://www.ebi.ac.uk/metabolights/)
  - [MetaboLights: a resource evolving in response to the needs of its scientific community](https://pubmed.ncbi.nlm.nih.gov/31691833/) (Flagship Publication)

To identify ML/AI publications, we used the MeSH terms:
- [Artificial Intelligence](https://www.ncbi.nlm.nih.gov/mesh/68001185) (OpenAlex Concept ID [C154945302](https://openalex.org/C154945302))
- [Machine Learning](https://www.ncbi.nlm.nih.gov/mesh/2010029) (OpenAlex Concept ID [C119857082](https://openalex.org/C119857082))

Machine learning is a subset of Artificial Intelligence, which is a class of algorithms. We can narrow down publications using datasets from one of these repositories and using machine learning by searching for papers citing the flagship papers for each repositroy, and narrowing the search to those including the MeSH terms mentioned above. We used the OpenAlex API and found that:
- 9 publications cite Metabolomics Workbench and are associated with the term ["Machine Learning"](https://api.openalex.org/works?filter=concepts.id:C119857082,cites:W1960974681) and 18 are associated with the term ["Artificial Intelligence"](https://api.openalex.org/works?filter=cites:W1960974681,concepts.id:C154945302) **How many are the same?**
- 4 publications cite MassIVE and are associated with the term ["Machine Learning"](https://api.openalex.org/works?filter=concepts.id:C119857082,cites:W2888985586) and 9 publications are associated with the term ["Artificial Intelligence"](https://api.openalex.org/works?filter=cites:W2888985586,concepts.id:C154945302). There were [9 unique papers](https://api.openalex.org/works?filter=cites:W2888985586,concepts.id:C154945302|C119857082) (**not sure if this API call gets what I am going for**)
- 



# Methods



## Gathering CFDE Citations and Publications

### Using the CFDE website

We gathered publications for a selection of target DCCs using the Common Fund [Publications Search by Program website](https://commonfund.nih.gov/publications?pid=0). We wrote a web scraping program to gather all the publications listed for the target programs, then used the [PubMed API](https://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EFetch_) and the [OpenAlex API](http://openalex.org/) to gather bibliometric data and save the results. 

### Using iCite

Note iCite has an API: https://icite.od.nih.gov/api

Sams methods here

## Bibliometric Analysis

What is the message we want to put with this section. 
For tomorrow:
- Focus on Kids First (and competing) and Metabolomics (and competing)
- informative, how have different DCCs/datasets been cited over time
- Jordan-- Measure the value of dataset by how often it is cited internal to the DCC vs external, based on affiliation of the last author. 

Kids First 
- TCGA/GDC 

Metabolomics
- MassIVE
- GNPS (UCSD)
- MetaboLights

Story:
The CFDE DCCs are tasked with creating FAIR datasets that will be used by the scientific community. One method of assessing the "value" of a dataset is by measuring the number of times that dataset or DCC has been cited in the literature compared to similar non-CFDE funded datasets or repositories. 
Here, we explored the citations of CFDE DCC datasets over time, identifying highly cited DCCs and compared them to "similar" dataset repositories to paint a better picture of where CFDE DCC datasets stand in relation to others in the field. 

For now, focus on Kids First and Metabolomics

- Plot 1 would be the target DCC citations over time (by keyword name of DCC, or citing flagship)
- Plot 2 internal to the DCC citing vs external to DCC citing, based on affiliation of last author
- Plot 3 would get into comparing it to similar repositories


