VENV_DIR := rand_venvi
PYTHON := $(VENV_DIR)/bin/python3
PIP := $(VENV_DIR)/bin/pip
HOST := $(shell grep '^host' app.ini | sed 's/host *= *//')
PORT := $(shell grep '^port' app.ini | sed 's/port *= *//')

.PHONY: all setup run clean

all: run

setup:
	python3 -m venv $(VENV_DIR) > /dev/null 2>&1
	$(PIP) install --upgrade pip > /dev/null 2>&1
	$(PIP) install flask pillow numpy > /dev/null 2>&1

run:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Not setup yet, setting up now..."; \
		$(MAKE) setup; \
	fi
	@echo "Starting app up !!"
	@echo "Access the app at $(HOST):$(PORT)"
	@$(PYTHON) src/SRC/app.py > /dev/null 2>&1

dbg:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Not setup yet, setting up now..."; \
		$(MAKE) setup; \
	fi
	@$(PYTHON) src/SRC/app.py

clean:
	rm -rf $(VENV_DIR)
