#!/bin/bash
set -e
# first, keywords
echo "Building keyword dataset"
python commonfund/keyword.py --keyword-key input/keyword-key.csv
echo "Adding iCite to keyword dataset"
python commonfund/icite.py --pmid-key keyword_results.json
echo "Adding OpenAlex to keyword dataset"
#python commonfund/openalex.py --icite-key keyword_icite_results.json

# repeat for Flagships and for CFDE Website
echo "Building Flagship dataset"
python commonfund/flagship.py --flagship-key input/flagships.csv
echo "Adding iCite to flagship dataset"
python commonfund/icite.py --pmid-key flagship_results.json
echo "Adding OpenAlex to the flagship dataset"
#python commonfund/openalex.py --icite-key flagship_icite_results.json

echo "Building CFDE citation dataset"
python commonfund/cfde.py --cfde-key input/cfde_programs_key.json
echo "Adding iCite to CFDE citation dataset"
python commonfund/icite.py --pmid-key cfde_results.json
#echo "Adding OpenAlex to the CFDE citation dataset"
#python commonfund/openalex.py --icite-key cfde_icite_results.json
