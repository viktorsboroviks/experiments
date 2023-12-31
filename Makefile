TOOLS_GIT = git@github.com:viktorsboroviks/tools.git
TOOLS_BRANCH = origin/main
TOOLS_PATH = tools
ENV_FIN = ./$(TOOLS_PATH)/scripts/env_fin.sh
PYTHONPATH := $(PYTHONPATH):$(TOOLS_PATH)/python:finance
RUN_PATH ?= $(PWD)

.PHONY: all \
	setup \
	setup-lint \
	clean \
	distclean \
	finance \
	test \
	lint

all: finance test lint

$(TOOLS_PATH):
	git clone $(TOOLS_GIT) $(TOOLS_PATH)
	cd $(TOOLS_PATH); git checkout $(TOOLS_BRANCH)

setup: $(TOOLS_PATH)
	make env-fin --directory $(TOOLS_PATH)

setup-lint: $(TOOLS_PATH)
	make env-lint --directory $(TOOLS_PATH)

finance: setup
	$(ENV_FIN) PYTHONPATH=$(PYTHONPATH) \
		python3 ./finance/run_alarm.py
	$(ENV_FIN) PYTHONPATH=$(PYTHONPATH) \
		python3 ./finance/run_price.py
	$(ENV_FIN) PYTHONPATH=$(PYTHONPATH) \
		python3 ./finance/run_comparison.py
	$(ENV_FIN) PYTHONPATH=$(PYTHONPATH) \
		python3 ./finance/run_sma_cross.py

test: setup
	$(ENV_FIN) PYTHONPATH=$(PYTHONPATH) \
		python3 -m pytest --capture=no ./tests/test_strategies.py

lint: setup-lint
	$(TOOLS_PATH)/scripts/lint.sh --hide-todo --verbose $(RUN_PATH)

# remove temporary files
clean:
	rm -rfv `find . -name __pycache__`
	rm -rfv `find . -name __vbfin_cache__`
	rm -rfv `find . -name *.svg`
	rm -rfv `find . -name *.html`

# remove all files produced by `make`
distclean: clean
	rm -rfv $(TOOLS_PATH)
