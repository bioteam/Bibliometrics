intermediate = data/intermediate/
final = data/final/


# $(final)keyword_icite_oa_results.json: $(intermediate)keyword_icite_results.json
# 	@echo "Running openalex for keywords"
# 	python commonfund/openalex.py --icite-key $(intermediate)keyword_icite_results.json --cache 

$(intermediate)keyword_icite_results.json: $(intermediate)keyword_results.json
	@echo "Running icite.py for keywords"
	python commonfund/icite.py --pmid-key $(intermediate)keyword_results.json

$(intermediate)keyword_results.json: input/keyword-key.csv
	@echo "Running keyword.py"
	python commonfund/keyword.py --keyword-key input/keyword-key.csv

# $(final)cfde_icite_oa_results.json: $(intermediate)cfde_icite_results.json
# 	@echo "Running openalex for cfde"
# 	python commonfund/openalex.py --icite-key $(intermediate)cfde_icite_results.json --cache 


$(intermediate)cfde_icite_results.json: $(intermediate)cfde_results.json
	@echo "Running icite.py for CFDE"
	python commonfund/icite.py --pmid-key $(intermediate)cfde_results.json

$(intermediate)cfde_results.json: input/cfde-programs-key.json
	@echo "Running cfde.py"
	python commonfund/cfde.py --cfde-key input/cfde-programs-key.json

$(intermediate)flagship_icite_results.json: $(intermediate)flagship_results.json
	@echo "Running icite.py for Flagships"
	python commonfund/icite.py --pmid-key $(intermediate)flagship_results.json

$(intermediate)flagship_results.json: input/flagships.csv
	@echo "Running flagship.py"
	python commonfund/flagship.py --flagship-key input/flagships.csv
