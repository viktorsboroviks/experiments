TOOLS_GIT = git@github.com:viktorsboroviks/tools.git
TOOLS_BRANCH = origin/main
TOOLS_PATH = tools
PYTHONPATH := $(PYTHONPATH):$(TOOLS_PATH)/python:finance
ENV_FIN = ./$(TOOLS_PATH)/scripts/env_fin.sh

.PHONY: all \
	setup \
	clean \
	distclean \
	test

all: test

$(TOOLS_PATH):
	git clone $(TOOLS_GIT) $(TOOLS_PATH)
	cd $(TOOLS_PATH); git checkout $(TOOLS_BRANCH)

setup: $(TOOLS_PATH)
	make env-fin --directory $(TOOLS_PATH)

test: setup
	$(ENV_FIN) PYTHONPATH=$(PYTHONPATH) \
		python3 -m pytest --capture=no ./tests/test_strategies.py

# remove temporary files
clean:
	rm -rfv `find . -name __pycache__`
	rm -rfv `find . -name __vbfin_cache__`
	rm -rfv `find . -name *.svg`
	rm -rfv `find . -name *.html`

# remove all files produced by `make`
distclean: clean
	rm -rfv $(TOOLS_PATH)
