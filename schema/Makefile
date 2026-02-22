# ==============================================================================
# Agent Skills JSON Schema
# ==============================================================================
#
# Quick start:
#   make check/deps                              # verify tooling
#   make test                                    # run schema tests
#   make test/samples                            # validate sample skills
#   make validate SKILL=path/to/my-skill         # validate a SKILL.md
#
# ==============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ==============================================================================
# Colors and Formatting
# ==============================================================================

ifneq ($(TERM),)
    RED    := $(shell tput setaf 1 2>/dev/null)
    GREEN  := $(shell tput setaf 2 2>/dev/null)
    YELLOW := $(shell tput setaf 3 2>/dev/null)
    CYAN   := $(shell tput setaf 6 2>/dev/null)
    BOLD   := $(shell tput bold 2>/dev/null)
    DIM    := $(shell tput dim 2>/dev/null)
    RESET  := $(shell tput sgr0 2>/dev/null)
else
    RED    :=
    GREEN  :=
    YELLOW :=
    CYAN   :=
    BOLD   :=
    DIM    :=
    RESET  :=
endif

CHECK := ✓
CROSS := ✗
WARN  := ⚠

# ==============================================================================
# Runtime detection
# ==============================================================================
# Detect available package managers. We only need existence here — the full
# symlink resolution happens in check/deps where we have proper bash.
# ==============================================================================

NPM  := $(shell command -v npm 2>/dev/null)
BUN  := $(shell command -v bun 2>/dev/null)
NODE := $(shell command -v node 2>/dev/null)

# Pick the package manager: prefer bun, fall back to npm
ifneq ($(BUN),)
    PM         := bun
    PM_INSTALL := $(BUN) install
    PM_TEST    := $(BUN) run test
else ifneq ($(NPM),)
    PM         := npm
    PM_INSTALL := $(NPM) install
    PM_TEST    := $(NPM) test
endif

SAMPLES := $(wildcard samples/*/SKILL.md)

# ==============================================================================
# Targets
# ==============================================================================

.PHONY: help check/deps test test/samples validate clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_/-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  $(CYAN)%-16s$(RESET) %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Resolve the real path behind a command, following all symlinks.
#
# Works on macOS (no GNU readlink -f) and Linux. Uses readlink in a loop,
# handling both absolute and relative symlink targets.
#
# Usage (inside a recipe):
#   REAL=$$(resolve_bin npm)
# ---------------------------------------------------------------------------
check/deps: ## Check required dependencies
	@resolve_bin() { \
		local bin; \
		bin=$$(command -v "$$1" 2>/dev/null) || return 1; \
		while [ -L "$$bin" ]; do \
			local dir; \
			dir=$$(cd "$$(dirname "$$bin")" && pwd -P); \
			local target; \
			target=$$(readlink "$$bin"); \
			case "$$target" in \
				/*) bin="$$target" ;; \
				*)  bin="$$dir/$$target" ;; \
			esac; \
		done; \
		echo "$$bin"; \
	}; \
	\
	echo "$(BOLD)Checking dependencies…$(RESET)"; \
	echo ""; \
	MISSING=0; \
	\
	NODE_BIN=$$(resolve_bin node); \
	if [ -n "$$NODE_BIN" ]; then \
		NODE_VER=$$($$NODE_BIN --version 2>/dev/null); \
		echo "  $(GREEN)$(CHECK)$(RESET) node $$NODE_VER  $(DIM)($$NODE_BIN)$(RESET)"; \
	else \
		echo "  $(RED)$(CROSS)$(RESET) node not found"; \
		echo "    $(YELLOW)→$(RESET) Install: https://nodejs.org/"; \
		MISSING=$$((MISSING + 1)); \
	fi; \
	\
	NPM_BIN=$$(resolve_bin npm); \
	if [ -n "$$NPM_BIN" ]; then \
		NPM_VER=$$($$NPM_BIN --version 2>/dev/null); \
		echo "  $(GREEN)$(CHECK)$(RESET) npm $$NPM_VER  $(DIM)($$NPM_BIN)$(RESET)"; \
	else \
		echo "  $(YELLOW)$(WARN)$(RESET)  npm not found"; \
	fi; \
	\
	NPX_BIN=$$(resolve_bin npx); \
	if [ -n "$$NPX_BIN" ]; then \
		NPX_VER=$$($$NPX_BIN --version 2>/dev/null); \
		echo "  $(GREEN)$(CHECK)$(RESET) npx $$NPX_VER  $(DIM)($$NPX_BIN)$(RESET)"; \
	else \
		echo "  $(YELLOW)$(WARN)$(RESET)  npx not found"; \
	fi; \
	\
	BUN_BIN=$$(resolve_bin bun); \
	if [ -n "$$BUN_BIN" ]; then \
		BUN_VER=$$($$BUN_BIN --version 2>/dev/null); \
		echo "  $(GREEN)$(CHECK)$(RESET) bun $$BUN_VER  $(DIM)($$BUN_BIN)$(RESET)"; \
	else \
		echo "  $(DIM)  - bun not installed (optional)$(RESET)"; \
	fi; \
	\
	BUNX_BIN=$$(resolve_bin bunx); \
	if [ -n "$$BUNX_BIN" ]; then \
		echo "  $(GREEN)$(CHECK)$(RESET) bunx  $(DIM)($$BUNX_BIN)$(RESET)"; \
	else \
		echo "  $(DIM)  - bunx not installed (optional)$(RESET)"; \
	fi; \
	\
	echo ""; \
	if [ -z "$$NPM_BIN" ] && [ -z "$$BUN_BIN" ]; then \
		echo "  $(RED)$(CROSS) No package manager found (need npm or bun)$(RESET)"; \
		MISSING=$$((MISSING + 1)); \
	else \
		PM_ACTIVE="npm"; \
		PM_PATH="$$NPM_BIN"; \
		if [ -n "$$BUN_BIN" ]; then PM_ACTIVE="bun"; PM_PATH="$$BUN_BIN"; fi; \
		echo "  $(GREEN)$(CHECK)$(RESET) Using $(BOLD)$$PM_ACTIVE$(RESET) as package manager  $(DIM)($$PM_PATH)$(RESET)"; \
	fi; \
	\
	echo ""; \
	if [ $$MISSING -eq 0 ]; then \
		echo "  $(GREEN)$(CHECK) All dependencies satisfied$(RESET)"; \
	else \
		echo "  $(RED)$(CROSS) $$MISSING required dependency(ies) missing$(RESET)"; \
		exit 1; \
	fi

node_modules: package.json
ifndef PM
	$(error No package manager found. Run 'make check/deps' for details)
endif
	@$(PM_INSTALL)
	@touch node_modules

test: node_modules ## Run schema tests
	@$(PM_TEST)

test/samples: node_modules ## Validate sample skills (from anthropics/skills)
	@for skill in $(SAMPLES); do \
		node validate.mjs "$$skill" || exit 1; \
	done

validate: node_modules ## Validate a SKILL.md (usage: make validate SKILL=path/to/skill)
	@if [ -z "$(SKILL)" ]; then \
		echo "Usage: make validate SKILL=path/to/skill-name"; \
		exit 1; \
	fi
	@node validate.mjs "$(SKILL)"

clean: ## Remove node_modules
	rm -rf node_modules
