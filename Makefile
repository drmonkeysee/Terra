PY := python3
VENV := venv
ACTIVATE := source $(VENV)/bin/activate

.PHONY: clean purge run

run: $(VENV)
	$(ACTIVATE) && $(PY) main.py

$(VENV):
	$(PY) -m venv $@
	$(ACTIVATE) && pip install -U pip setuptools wheel

clean:
	find . -type d -path ./$(VENV) -prune -o -name __pycache__ -exec $(RM) -r {} +

purge: clean
	$(RM) -r $(VENV)
