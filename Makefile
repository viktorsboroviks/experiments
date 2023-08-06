TOOLS_GIT = git@github.com:viktorsboroviks/tools.git
TOOLS_BRANCH = v1.4
TOOLS_PATH = tools

.PHONY: all finance setup clean distclean
all: finance

$(TOOLS_PATH):
	git clone $(TOOLS_GIT) $(TOOLS_PATH)
	cd $(TOOLS_PATH); git checkout $(TOOLS_BRANCH)

setup: $(TOOLS_PATH)
	make setup-fin setup-lint --directory $(TOOLS_PATH)

#finance:

#performance-test: setup
# generates new .svg images under ./python
#	cd python; ../$(TOOLS_PATH)/docker/finpy.sh performance_test.py

# remove temporary files
clean:
	rm -rfv `find . -name __pycache__`
	rm -rfv `find . -name __vbfin_cache__`
	rm -rfv `find . -name *.svg`

# remove all files produced by `make`
distclean: clean
	rm -rfv $(TOOLS_PATH)
