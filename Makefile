#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = decea
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python3

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	uv sync


## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	uv run ruff format --check
	uv run ruff check

## Format source code with ruff
.PHONY: format
format:
	uv run ruff check --fix
	uv run ruff format


## Run tests
.PHONY: test
test:
	uv run pytest tests


## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	uv venv --python $(PYTHON_VERSION)
	@echo ">>> New uv virtual environment created. Activate with:"
	@echo ">>> Unix/macOS: source ./.venv/bin/activate"


#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Save a snapshot of the current NOTAMs (schedule it daily to build a history)
.PHONY: notam
notam:
	uv run python -c "from module_decea.dataset import coletar_notam; coletar_notam()"


# Daily NOTAM collection via cron. Another hour: make agendar_notam NOTAM_HORA=12
NOTAM_HORA ?= 9
NOTAM_LOG ?= $(HOME)/Library/Logs/decea-coleta-notam.log
NOTAM_CRON = 0 $(NOTAM_HORA) * * * $(CURDIR)/.venv/bin/python -c "from module_decea.dataset import coletar_notam; coletar_notam()" >> $(NOTAM_LOG) 2>&1

## Schedule the daily NOTAM collection in cron (at 9h unless NOTAM_HORA is given)
.PHONY: agendar_notam
agendar_notam: requirements
	mkdir -p $(dir $(NOTAM_LOG))
	(crontab -l 2>/dev/null | grep -v -e coletar_notam -e '^# decea'; \
	 echo '# decea: coleta diária de NOTAMs (remover com make desagendar_notam)'; \
	 echo '$(NOTAM_CRON)') | crontab -
	crontab -l

## Remove the daily NOTAM collection from cron
.PHONY: desagendar_notam
desagendar_notam:
	crontab -l 2>/dev/null | grep -v -e coletar_notam -e '^# decea' | crontab -
	@echo ">>> Coleta de NOTAMs removida do cron"


#################################################################################
# Self Documenting Commands                                                    #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
