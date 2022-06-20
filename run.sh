#!/bin/bash
set -e
# first, keywords
echo "Building keyword dataset"
python commonfund/keyword.py --keyword-key input/keyword-key.csv
echo "Adding iCite to keyword dataset"
python commonfund/icite.py --pmid-key keyword_results.json
echo "Adding OpenAlex to keyword dataset"
echo "TODO"

# repeat for Flagships and for CFDE Website

