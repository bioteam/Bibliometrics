# get pmids for papers using a DCC/project as a keyword
from pprint import pprint
import requests

# https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch


def respose_to_json(xml_content):
    pass


def build_esearch_url(short_name, long_name=None):
    end_portion = "+NOT+(Review[Publication Type])&retmax=100000&retmode=json"
    short_portion = f'("{short_name}"[Title/Abstract]+OR+"{short_name}"[Text Word]'
    if long_name:
        long_portion = f'"+OR+{long_name}"[Title/Abstract]+OR+"{long_name}"[Text Word])'
    else:
        long_portion = ")"
    return f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={short_portion}{long_portion}{end_portion}"
