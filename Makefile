.PHONY: help doc serve release
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
	@echo "    serve: Serve documentation on http://localhost:8000"
	@echo "    release: Build and upload the package to PyPi"

# Sphinx documentation targets
serve: html
	@cd $(BUILDDIR) && python -m http.server 8000

# Catch-all target: route all unknown targets to Sphinx using the "make" target
%: Makefile
	@$(SPHINXBUILD) -M $@ $(ALLSPHINXOPTS) $(BUILDDIR)

# PyPi release chain
release: clean setup build upload

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	pip install --upgrade build twine

clean:
	rm -rf dist

build:
	.venv/bin/python3 -m build

upload:
	.venv/bin/python3 -m twine upload --repository pypi dist/*