SHELL := /bin/bash
.DEFAULT_GOAL := help

# ==============================================================================
# Agent Skills JSON Schema — Development targets
# ==============================================================================
#
# Quick start:
#   make test                                    # run schema tests
#   make test/samples                            # validate sample skills
#   make validate SKILL=path/to/my-skill         # validate a SKILL.md
#
# Without make (npx / bunx):
#   cd schema && npx --yes -p ajv -p yaml node validate.mjs path/to/SKILL.md
#   cd schema && npm install && npm test
#
# ==============================================================================

SAMPLES := $(wildcard samples/*/SKILL.md)

.PHONY: help test test/samples validate clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_/-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

node_modules: package.json
	npm install
	@touch node_modules

test: node_modules ## Run schema tests
	npm test

test/samples: node_modules ## Validate sample skills (from anthropics/skills)
	@for skill in $(SAMPLES); do \
		node validate.mjs "$$skill" || exit 1; \
	done

validate: node_modules ## Validate a SKILL.md (usage: make validate SKILL=path/to/skill)
	@if [ -z "$(SKILL)" ]; then \
		echo "Usage: make validate SKILL=path/to/skill-name"; \
		exit 1; \
	fi
	node validate.mjs "$(SKILL)"

clean: ## Remove node_modules
	rm -rf node_modules
