TOOLS_GIT = git@github.com:viktorsboroviks/tools.git
TOOLS_BRANCH = v1.6
TOOLS_PATH = tools

.PHONY: all \
	setup \
	clean \
	distclean \
	run-experiments \
	run-finance

all: run-experiments

$(TOOLS_PATH):
	git clone $(TOOLS_GIT) $(TOOLS_PATH)
	cd $(TOOLS_PATH); git checkout $(TOOLS_BRANCH)

setup: $(TOOLS_PATH)
	make env-fin --directory $(TOOLS_PATH)

run-experiments: run-finance

#run-finance: setup
#	cd finance/1_simple_examples; ../../$(TOOLS_PATH)/scripts/env_fin.sh \
#		python3 backtest_plotly.py
#	cd finance/1_simple_examples; ../../$(TOOLS_PATH)/scripts/env_fin.sh \
#		python3 backtest_vbplot.py

# remove temporary files
clean:
	rm -rfv `find . -name __pycache__`
	rm -rfv `find . -name __vbfin_cache__`
	rm -rfv `find . -name *.svg`

# remove all files produced by `make`
distclean: clean
	rm -rfv $(TOOLS_PATH)
