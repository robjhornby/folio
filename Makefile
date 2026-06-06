PAGES_DIR := pages
SITE_DIR := _site
MARIMO_PORT ?= 2719
SERVE_PORT ?= 8000
PAGE ?=
PAGES := $(wildcard $(PAGES_DIR)/*.py)
PAGE_NAMES := $(basename $(notdir $(PAGES)))
REQUESTED_PAGE := $(or $(PAGE),$(word 2,$(MAKECMDGOALS)))
REQUESTED_PAGE_FILE := $(if $(REQUESTED_PAGE),$(if $(filter $(PAGES_DIR)/%.py %.py,$(REQUESTED_PAGE)),$(REQUESTED_PAGE),$(PAGES_DIR)/$(REQUESTED_PAGE).py))

.PHONY: help list-pages edit stop-edit restart-edit check build serve stop-serve restart-serve clean $(PAGE_NAMES)

help:
	@printf "Available commands:\n"
	@printf "  make list-pages       List publishable marimo pages\n"
	@printf "  make edit name        Edit/run a marimo page locally\n"
	@printf "  make stop-edit        Stop marimo on MARIMO_PORT\n"
	@printf "  make restart-edit name  Stop then edit/run a marimo page locally\n"
	@printf "  make check            Compile-check all marimo pages\n"
	@printf "  make build            Build the static GitHub Pages site\n"
	@printf "  make serve            Serve the built site locally\n"
	@printf "  make stop-serve       Stop the local static server on SERVE_PORT\n"
	@printf "  make restart-serve    Stop then serve the built site locally\n"
	@printf "  make clean            Remove generated site output\n"

list-pages:
	@for page in $(PAGES); do \
		name="$$(basename "$${page%.py}")"; \
		printf "%s -> /%s/\n" "$$page" "$$name"; \
	done

edit:
	@if [ -z "$(REQUESTED_PAGE)" ]; then \
		$(MAKE) --no-print-directory list-pages; \
	else \
		if [ ! -f "$(REQUESTED_PAGE_FILE)" ]; then \
			printf "Page not found: $(REQUESTED_PAGE)\n\n" >&2; \
			$(MAKE) --no-print-directory list-pages >&2; \
			exit 2; \
		fi; \
		pids="$$(lsof -tiTCP:$(MARIMO_PORT) -sTCP:LISTEN)"; \
		if [ -n "$$pids" ]; then \
			printf "Port $(MARIMO_PORT) is already in use by: %s\n" "$$pids" >&2; \
			printf "Run 'make restart-edit $(REQUESTED_PAGE)' to stop it and reopen this page.\n" >&2; \
			exit 2; \
		fi; \
		uvx marimo edit "$(REQUESTED_PAGE_FILE)" --sandbox --watch --host 127.0.0.1 --port $(MARIMO_PORT); \
	fi

stop-edit:
	@pids="$$(lsof -tiTCP:$(MARIMO_PORT) -sTCP:LISTEN)"; \
	if [ -n "$$pids" ]; then \
		printf "Stopping marimo server(s) on port $(MARIMO_PORT): %s\n" "$$pids"; \
		kill $$pids; \
		sleep 1; \
		pids="$$(lsof -tiTCP:$(MARIMO_PORT) -sTCP:LISTEN)"; \
		if [ -n "$$pids" ]; then \
			printf "Force stopping marimo server(s) on port $(MARIMO_PORT): %s\n" "$$pids"; \
			kill -9 $$pids; \
		fi; \
	else \
		printf "No marimo server listening on port $(MARIMO_PORT)\n"; \
	fi

restart-edit: stop-edit edit

$(PAGE_NAMES):
	@:

check:
	uv run --isolated --no-project --python '>=3.12' python -m py_compile $(PAGES)

build: clean
	mkdir -p $(SITE_DIR)
	cp index.html $(SITE_DIR)/index.html
	@for page in $(PAGES); do \
		name="$$(basename "$${page%.py}")"; \
		printf "Exporting %s -> /%s/\n" "$$page" "$$name"; \
		uvx marimo export html-wasm --sandbox "$$page" -o "$(SITE_DIR)/$$name" --mode run --no-show-code; \
	done
	find $(SITE_DIR) -name .DS_Store -type f -delete

serve:
	@printf "Serving site at:\n"
	@printf "  http://127.0.0.1:$(SERVE_PORT)/\n"
	uv run --isolated --no-project --python '>=3.12' python -m http.server $(SERVE_PORT) --directory $(SITE_DIR)

stop-serve:
	@pids="$$(lsof -tiTCP:$(SERVE_PORT) -sTCP:LISTEN)"; \
	if [ -n "$$pids" ]; then \
		printf "Stopping server(s) on port $(SERVE_PORT): %s\n" "$$pids"; \
		kill $$pids; \
		sleep 1; \
		pids="$$(lsof -tiTCP:$(SERVE_PORT) -sTCP:LISTEN)"; \
		if [ -n "$$pids" ]; then \
			printf "Force stopping server(s) on port $(SERVE_PORT): %s\n" "$$pids"; \
			kill -9 $$pids; \
		fi; \
	else \
		printf "No server listening on port $(SERVE_PORT)\n"; \
	fi

restart-serve: stop-serve serve

clean:
	uv run --isolated --no-project --python '>=3.12' python -c "import shutil; shutil.rmtree('$(SITE_DIR)', ignore_errors=True)"
