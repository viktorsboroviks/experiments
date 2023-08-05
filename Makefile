TOOLS_GIT = git@github.com:viktorsboroviks/tools.git
TOOLS_BRANCH = v1.3
TOOLS_PATH = tools

.PHONY: all setup clean distclean
all: 

$(TOOLS_PATH):
	git clone $(TOOLS_GIT) $(TOOLS_PATH)
	cd $(TOOLS_PATH); git checkout $(TOOLS_BRANCH)

setup: $(TOOLS_PATH)
	make setup-fin setup-lint --directory $(TOOLS_PATH)

#performance-test: setup
# generates new .svg images under ./python
#	cd python; ../$(TOOLS_PATH)/docker/finpy.sh performance_test.py

# remove temporary files
#clean:
#	rm -rfv __pycache__ python/__pycache__

# remove all files produced by `make`
distclean: clean
	rm -rfv $(TOOLS_PATH)
