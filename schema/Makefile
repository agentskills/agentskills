SHELL := /bin/bash
.DEFAULT_GOAL := help

# ==============================================================================
# Agent Skills JSON Schema — Development targets
# ==============================================================================

.PHONY: help install test clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_/-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: node_modules ## Install dependencies

node_modules: package.json
	npm install
	@touch node_modules

test: node_modules ## Run schema tests
	npm test

clean: ## Remove node_modules
	rm -rf node_modules
