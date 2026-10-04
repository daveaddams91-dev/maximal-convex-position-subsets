PY ?= python
N ?= 9
AAK_BASE := http://www.ist.tugraz.at/staff/aichholzer/research/rp/triangulations/ordertypes/data

.PHONY: help install test numbers figures paper fetch-data clean lint

help:
	@echo "make install    - install the package in editable mode with dev extras"
	@echo "make fetch-data - download the Aichholzer-Aurenhammer-Krasser order-type database"
	@echo "make test       - run the fast correctness test suite"
	@echo "make numbers    - recompute every number quoted in the paper (slow)"
	@echo "make figures    - regenerate the figures"
	@echo "make paper      - compile paper/main.tex (requires pdflatex)"
	@echo "make clean      - remove caches and generated results"

install:
	$(PY) -m pip install -e ".[dev,plots]"

fetch-data:
	@mkdir -p data/ordertypes
	@for n in 03 04 05 06 07 08 09; do \
	  f=otypes$$n.b08; \
	  if [ ! -f data/ordertypes/$$f ]; then \
	    echo "fetching $$f"; \
	    curl -fsSL -o data/ordertypes/$$f $(AAK_BASE)/$$f; \
	  fi; \
	done

test:
	$(PY) -m pytest tests -v

numbers:
	$(PY) experiments/run_f_aak.py $(N) f_aak.json
	$(PY) experiments/reproduce_paper_numbers.py

figures:
	$(PY) experiments/make_figures.py

paper:
	cd paper && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex

lint:
	$(PY) -m compileall -q src experiments tests

clean:
	rm -rf .pytest_cache **/__pycache__ figures/*.png results/ordertype_cache
	find . -name "*.pyc" -delete