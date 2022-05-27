# Bibliometrics exploration
The Google Sheet with Sam's research https://docs.google.com/spreadsheets/d/1zmx-wxmOgWTC2lrmaDXcZ-KN6R2MdCzq8udqFgPWfAA/edit#gid=552619060

The DCC's funded by CFDE create numerous datasets used and cited throughout the scientific community. We will refer to papers written "about" the DCC and cited in subsequent works as "Flagship Publications". For example, the [4D Nucleome project's](https://pubmed.ncbi.nlm.nih.gov/28905911/) flagship paper describes the consortium, methods, and goals. [196 publications](https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=28905911) cited the 4D nucleome project. To identify each DCC's flagship publications, we...

DESCRIBE METHODS SAM USED TO IDENTIFY FLAGSHIP PAPERS

Publications resulting from datasets produced by DCCs are more difficult to track. In the easy case, they may cite the dataset or flagship paper, allowing us to efficiently credit the DCC for the publication. However, some may simply Acknowledge the DCC dataset or producing researcher, and sometimes the data set name can only be found as a keyword search, making complete tracking difficult. We used the following methods to build a comprehensive list of papers mentioned in each program:

METHODS FOR TRACKING PAPERS

# Directions to explore

Which CFDE repository is most AI ready?

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

