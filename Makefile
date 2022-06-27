.POSIX:

.PHONY: clean help

venv/code-run: source_code_normalizer.py test.py tests/* venv/bin/activate ## Run tests.
	./venv/bin/python test.py
	touch venv/code-run

clean: ## Remove dependent directories.
	rm -rf __pycache__/ source_code_normalizer.egg-info/ tests/__pycache__/ venv/

help: ## Show all commands.
	@grep '##' $(MAKEFILE_LIST) | grep -v grep | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s# %s\n", $$1, $$2}'

venv/bin/activate: setup.cfg setup.py source_code_normalizer.py
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install --editable .
