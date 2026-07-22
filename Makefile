.PHONY: help doc
SHELL := /bin/bash

help:
	@echo "lvpyioTools"
	@echo "Usage: make [target]"
	@echo "Available targets:"
	@echo "    doc: Generate doc"

doc:
	.venv/bin/python ./doc/generate.py