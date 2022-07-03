PY := python3
SRC_DIR := src
VENV := venv
ACTIVATE := source $(VENV)/bin/activate
PRODUCT := terra
DOCF ?=
DOCT ?= $(PRODUCT)

.PHONY: clean doc int purge run

run: $(VENV)
	$(ACTIVATE) && PYTHONPATH=$(SRC_DIR) $(PY) -m $(PRODUCT)

int: $(VENV)
	$(ACTIVATE) && PYTHONPATH=$(SRC_DIR) $(PY)

doc: $(VENV)
	$(ACTIVATE) && PYTHONPATH=$(SRC_DIR) pydoc $(DOCF) $(DOCT)

$(VENV):
	$(PY) -m venv $@
	$(ACTIVATE) && pip install -U pip setuptools wheel

clean:
	find . -type d -path ./$(VENV) -prune -o -name __pycache__ -exec $(RM) -r {} +

purge: clean
	$(RM) -r $(VENV)
