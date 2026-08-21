# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
PAPER         ?=
BUILDDIR      ?= _build

# Internal variables.
PAPEROPT_letter = -D latex_paper_size=letter
PAPEROPT_a4     = -D latex_paper_size=a4
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
.PHONY: help Makefile

# Put it first so that "make help" is always the first target.
help:
	@$(SPHINXBUILD) -M help $(ALLSPHINXOPTS) $(BUILDDIR)

.PHONY: serve
serve: html
	@cd $(BUILDDIR) && python -m http.server 8000

# Catch-all target: route all unknown targets to Sphinx using the "make" target
# with the same name.
%: Makefile
	@$(SPHINXBUILD) -M $@ $(ALLSPHINXOPTS) $(BUILDDIR)
