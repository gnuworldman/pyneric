# Makefile for the Python pyneric project
# This has only been tested with GNU make from within the project root.

SHELL := /bin/bash

all: coverage build doc

flake:
	flake8 src

test: flake
	PYTHONPATH=src:tests coverage run --branch --module unittest discover
	PYTHONPATH=src python -m doctest docs/examples.rst

coverage: test
	coverage report -m

coverage_html: test
	coverage html

build:
	./setup.py build

readme:
	cat README_editable.rst | ( while read; do if [[ $${REPLY#.. include:: } != $${REPLY} ]]; then cat $${REPLY#.. include:: }; else echo $${REPLY}; fi; done ) > README.rst

doc: readme
	$(MAKE) -C docs html

clean:
	./setup.py clean -a
	$(MAKE) -C docs clean
	$(RM) MANIFEST
	$(RM) -r dist
	$(RM) -r htmlcov
	coverage erase
	find . -type d -name '__pycache__' | xargs $(RM) -r
	find . -type f -name '*.py[co]' | xargs $(RM)
#	git submodule update docs/_build/html
#	git -C docs/_build/html checkout gh-pages

.PHONY: test coverage coverage_html build readme doc clean
