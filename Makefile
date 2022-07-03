PY := python3
SRC_DIR := src
VENV := venv
ACTIVATE := source $(VENV)/bin/activate
PRODUCT := terra
DOCF ?=
DOCT ?= $(PRODUCT)
CLEAN_ASSETS := find . -type d -path ./$(VENV) -prune -o \
	\( -name __pycache__ -o -name .mypy_cache \)

.PHONY: clean doc dryclean int purge run type

run: $(VENV)
	$(ACTIVATE) && PYTHONPATH=$(SRC_DIR) $(PY) -m $(PRODUCT)

int: $(VENV)
	$(ACTIVATE) && PYTHONPATH=$(SRC_DIR) $(PY)

doc: $(VENV)
	$(ACTIVATE) && PYTHONPATH=$(SRC_DIR) pydoc $(DOCF) $(DOCT)

type: $(VENV)
	$(ACTIVATE) && MYPYPATH=$(SRC_DIR) mypy -p $(PRODUCT)

$(VENV):
	$(PY) -m venv $@
	$(ACTIVATE) && pip install -U pip setuptools wheel \
		&& pip install -r requirements.txt

dryclean:
	$(CLEAN_ASSETS) -print

clean:
	$(CLEAN_ASSETS) -exec $(RM) -r {} +

purge: clean
	$(RM) -r $(VENV)
