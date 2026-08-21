.PHONY: help doc serve
SHELL := /bin/bash

# Sphinx documentation variables
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
PAPER         ?=
BUILDDIR      ?= docs/_build

# Internal variables for Sphinx
PAPEROPT_letter = -D latex_paper_size=letter
PAPEROPT_a4     = -D latex_paper_size=a4
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs

help:
	@echo "lvpyioTools"
	@echo "Usage: make [target]"
	@echo "Available targets:"
	@echo "    doc: Generate doc"
	@echo "    serve: Serve documentation on http://localhost:8000"

doc:
	.venv/bin/python ./doc/generate.py

# Sphinx documentation targets
serve: html
	@cd $(BUILDDIR) && python -m http.server 8000

# Catch-all target: route all unknown targets to Sphinx using the "make" target
%: Makefile
	@$(SPHINXBUILD) -M $@ $(ALLSPHINXOPTS) $(BUILDDIR)