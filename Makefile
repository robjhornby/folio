NOTEBOOK := pages/factorial_estimation.py
SITE_DIR := _site
MARIMO_PORT ?= 2719
SERVE_PORT ?= 8000

.PHONY: help run check build serve stop-serve restart-serve clean

help:
	@printf "Available commands:\n"
	@printf "  make run     Run the marimo notebook locally\n"
	@printf "  make check   Compile-check the notebook Python\n"
	@printf "  make build   Build the static GitHub Pages site\n"
	@printf "  make serve   Serve the built site locally\n"
	@printf "  make stop-serve     Stop the local static server on SERVE_PORT\n"
	@printf "  make restart-serve  Stop then serve the built site locally\n"
	@printf "  make clean   Remove generated site output\n"

run:
	uvx marimo run $(NOTEBOOK) --sandbox --host 127.0.0.1 --port $(MARIMO_PORT)

check:
	uv run --isolated --no-project --python '>=3.12' python -m py_compile $(NOTEBOOK)

build: clean
	mkdir -p $(SITE_DIR)
	cp index.html $(SITE_DIR)/index.html
	uvx marimo export html-wasm --sandbox $(NOTEBOOK) -o $(SITE_DIR)/factorial-estimation --mode run --no-show-code
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
	else \
		printf "No server listening on port $(SERVE_PORT)\n"; \
	fi

restart-serve: stop-serve serve

clean:
	uv run --isolated --no-project --python '>=3.12' python -c "import shutil; shutil.rmtree('$(SITE_DIR)', ignore_errors=True)"
