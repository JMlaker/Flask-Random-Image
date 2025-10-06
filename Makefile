VENV_DIR := rand_venvi
PYTHON := $(VENV_DIR)/bin/python3
PIP := $(VENV_DIR)/bin/pip

.PHONY: all setup run clean

all: run

setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install flask pillow numpy

run:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Not setup yet, setting up now..."; \
		$(MAKE) setup; \
	fi
	$(PYTHON) src/SRC/app.py

clean:
	rm -rf $(VENV_DIR)
